---
title: "Multi-modal RAG: Searching Through Images and Text Together"
categories:
    - Tech
tags:
    - ai
    - rag
    - multimodal
    - python
    - learning
toc: true
---

Standard RAG pipelines treat your document corpus as text. But a lot of the actual information in technical documentation, research papers, and slide decks lives in figures, tables, and diagrams. When a user asks "show me the architecture diagram from the deployment guide," a text-only RAG system has no answer. Extending RAG to handle images alongside text is one of the more interesting engineering problems I've dug into recently.

## The Core Problem: Shared Embedding Space

To search across both modalities, you need embeddings that are comparable — a text query should be able to retrieve a relevant image. CLIP (Contrastive Language-Image Pretraining) solves this by training image and text encoders jointly on matched pairs, mapping both into the same vector space.

```python
from transformers import CLIPProcessor, CLIPModel
import torch
from PIL import Image

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def embed_image(image_path: str) -> list[float]:
    image = Image.open(image_path).convert("RGB")
    inputs = processor(images=image, return_tensors="pt")
    with torch.no_grad():
        features = model.get_image_features(**inputs)
    return features[0].tolist()

def embed_text(text: str) -> list[float]:
    inputs = processor(text=[text], return_tensors="pt", padding=True)
    with torch.no_grad():
        features = model.get_text_features(**inputs)
    return features[0].tolist()
```

This gives you 512-dimensional embeddings where cosine similarity between image and text embeddings is meaningful. A text query "network latency graph" will have high similarity to an image of a latency time-series chart.

## Getting Images Out of PDFs

Most documents come as PDFs. Extracting images is the unglamorous step nobody talks about:

```python
import fitz  # PyMuPDF
from pathlib import Path

def extract_images_from_pdf(pdf_path: str, output_dir: str) -> list[dict]:
    doc = fitz.open(pdf_path)
    images = []
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    for page_num, page in enumerate(doc):
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            ext = base_image["ext"]
            filename = output_path / f"page{page_num}_img{img_index}.{ext}"
            filename.write_bytes(image_bytes)
            images.append({
                "path": str(filename),
                "page": page_num,
                "source": pdf_path,
            })
    return images
```

## ColPali and Captioning Strategies

CLIP embeddings capture visual semantics but lose fine-grained detail — a screenshot of a config file embeds similarly to any text-heavy image. Two better options depending on your setup:

**ColPali** (a recent approach) embeds document pages as images using a vision-language model, enabling direct page retrieval without OCR or text extraction. It handles charts, tables, and code screenshots well.

**Caption-then-embed**: Use GPT-4V or a local VLM to generate a description of each image, then embed the caption with your standard text embedder. Slower during indexing but lets you use the same text embedding model everywhere.

```python
from openai import OpenAI
import base64

client = OpenAI()

def caption_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}},
                {"type": "text", "text": "Describe this image in detail, focusing on what information it conveys. Be specific about any charts, diagrams, code, or data shown."}
            ]
        }],
        max_tokens=300,
    )
    return response.choices[0].message.content
```

## Storing and Retrieving Across Modalities

In Qdrant, you can store both image and text embeddings in the same collection by tagging each point with a payload indicating its type:

```python
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance

client = QdrantClient(":memory:")

client.create_collection(
    collection_name="docs",
    vectors_config=VectorParams(size=512, distance=Distance.COSINE),
)

# Index a text chunk
client.upsert("docs", points=[
    PointStruct(
        id=1,
        vector=embed_text("Network latency spikes under load"),
        payload={"type": "text", "content": "Network latency spikes under load...", "source": "guide.pdf", "page": 3},
    )
])

# Index an image
caption = caption_image("page3_img0.png")
client.upsert("docs", points=[
    PointStruct(
        id=2,
        vector=embed_text(caption),  # embed the caption, not raw image
        payload={"type": "image", "caption": caption, "path": "page3_img0.png", "source": "guide.pdf", "page": 3},
    )
])
```

At query time, embed the query with the same text encoder, retrieve top-k results, and handle image results by returning the image file path for rendering in your UI.

## What Still Doesn't Work Well

Retrieval accuracy drops significantly for images with dense text (code screenshots, tables). The caption quality bottleneck is real — a bad GPT-4V description produces a bad embedding. Indexing costs are also non-trivial if you're captioning thousands of images at vision model prices.

The setup is worthwhile if your documents are genuinely visual-heavy. For mostly-text documents with the occasional diagram, the added complexity probably isn't worth it.
