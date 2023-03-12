# This script reads all the markdown files in a given directory,
# collects the values of 'tags' in the front matter yaml and list
# them. Uses https://github.com/eyeseast/python-frontmatter package
# to read the front matter.

import sys
import glob
import frontmatter

# Get the directory path from the command line argument
if len(sys.argv) != 2:
    print("Usage: python3 list_tags.py [directory_path]")
    sys.exit(1)
directory_path = sys.argv[1]

# List all markdown files in the directory
markdown_files = glob.glob(f"{directory_path}/*.md")

# Collect all the tags from the markdown files
tags = []
for file in markdown_files:
    post = frontmatter.load(file)
    tags += post.get('tags', [])

# Sort and list the unique tags
unique_tags = sorted(list(set(tags)))
for tag in unique_tags:
    print(tag)
