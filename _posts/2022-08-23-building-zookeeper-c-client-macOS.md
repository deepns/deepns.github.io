---
title: Building Zookeeper C-Client on macOS
category:
    - Tech
tags:
    - zookeeper
    - macOS
    - programming
header:
  image: /assets/images/headers/building-zookeeper-on-macOS.jpg
  caption: "Photo Credit: [Clément Hélardot](https://unsplash.com/@clemhlrdt) on [Unsplash](https://unsplash.com/photos/95YRwf6CNw8)"
  teaser: /assets/images/teasers/building-zookeeper-on-macOS.jpg
---

Trying to build zookeeper c-client on macOS.

- Pulled the repo from [GitHub](https://github.com/apache/zookeeper)
- Followed the instructions from [here](https://github.com/apache/zookeeper) and [c-client](https://github.com/apache/zookeeper/tree/master/zookeeper-client/zookeeper-client-c)
- Installed maven through homebrew (`brew install mvn`)
- Built the source using `mvn clean build`

```console
[ERROR] Failures:
[ERROR]   ClientRequestTimeoutTest.testClientRequestTimeout:66 waiting for server 2 being up ==> expected: <true> but was: <false>
[ERROR]   KerberosTicketRenewalTest.shouldRecoverIfKerberosNotAvailableForSomeTime:187->access$100:57->assertEventually:216 execution exceeded timeout of 15000 ms by 18302 ms
[ERROR]   QuorumPeerMainTest.testLeaderElectionWithDisloyalVoter_stillHasMajority:1190->testLeaderElection:1237 Server 1 should have joined quorum by now ==> expected: <true> but was: <false
>
[ERROR]   ReconfigBackupTest.testVersionOfDynamicFilename:287 waiting for server 3 being up ==> expected: <true> but was: <false>
[ERROR]   ReconfigRollingRestartCompatibilityTest.testRollingRestartWithExtendedMembershipConfig:232 waiting for server 1 being up ==> expected: <true> but was: <false>
[ERROR] Errors:
[ERROR]   SaslAuthTest.testThreadsShutdownOnAuthFailed:219 » Timeout Failed to connect t...
[ERROR]   CnxManagerTest.testCnxManagerListenerThreadConfigurableRetry:309 » Bind Addres...
[ERROR]   DisconnectedWatcherTest.testManyChildWatchersAutoReset » Timeout testManyChild...
[INFO]
[ERROR] Tests run: 2982, Failures: 5, Errors: 3, Skipped: 4
[INFO]
[INFO] ------------------------------------------------------------------------
[INFO] Reactor Summary for Apache ZooKeeper 3.9.0-SNAPSHOT:
[INFO]
[INFO] Apache ZooKeeper ................................... SUCCESS [  3.114 s]
[INFO] Apache ZooKeeper - Documentation ................... SUCCESS [  1.328 s]
[INFO] Apache ZooKeeper - Jute ............................ SUCCESS [ 11.209 s]
[INFO] Apache ZooKeeper - Server .......................... FAILURE [27:17 min]
[INFO] Apache ZooKeeper - Metrics Providers ............... SKIPPED
[INFO] Apache ZooKeeper - Prometheus.io Metrics Provider .. SKIPPED
[INFO] Apache ZooKeeper - Client .......................... SKIPPED
[INFO] Apache ZooKeeper - Recipes ......................... SKIPPED
[INFO] Apache ZooKeeper - Recipes - Election .............. SKIPPED
[INFO] Apache ZooKeeper - Recipes - Lock .................. SKIPPED
[INFO] Apache ZooKeeper - Recipes - Queue ................. SKIPPED
[INFO] Apache ZooKeeper - Assembly ........................ SKIPPED
[INFO] Apache ZooKeeper - Compatibility Tests ............. SKIPPED
[INFO] Apache ZooKeeper - Compatibility Tests - Curator ... SKIPPED
[INFO] ------------------------------------------------------------------------
[INFO] BUILD FAILURE
[INFO] ------------------------------------------------------------------------
[INFO] Total time:  27:33 min
[INFO] Finished at: 2022-08-21T21:43:17-04:00
[INFO] ------------------------------------------------------------------------
[ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:2.22.1:test (default-test) on project zookeeper: There are test failures.
[ERROR]
```

It failed in running some unit tests on the Zookeeper server. Learnt from [here](https://issues.apache.org/jira/browse/ZOOKEEPER-3879?jql=project%20%3D%20ZOOKEEPER%20AND%20status%20%3D%20Open%20AND%20component%20%3D%20%22c%20client%22) that unit tests can be flaky sometimes. Retried the build with `mvn clean install -Pfull-build -DskipTests`. Failed again


```console
main:
    [mkdir] Created dir: /Users/deepan/workspace/github/zookeeper/zookeeper-client/zookeeper-client-c/target/c
[INFO] Executed tasks
[INFO]
[INFO] --- exec-maven-plugin:1.6.0:exec (autoreconf) @ zookeeper-client-c ---
[ERROR] Command execution failed.
java.io.IOException: Cannot run program "autoreconf" (in directory "/Users/deepan/workspace/github/zookeeper/zookeeper-client/zookeeper-client-c"): error=2, No such file or directory
    at java.lang.ProcessBuilder.start (ProcessBuilder.java:1143)
    at java.lang.ProcessBuilder.start (ProcessBuilder.java:1073)
    at java.lang.Runtime.exec (Runtime.java:615)
    at org.apache.commons.exec.launcher.Java13CommandLauncher.exec (Java13CommandLauncher.java:61)
    at org.apache.commons.exec.DefaultExecutor.launch (DefaultExecutor.java:279)
    at org.apache.commons.exec.DefaultExecutor.executeInternal (DefaultExecutor.java:336)
    at org.apache.commons.exec.DefaultExecutor.execute (DefaultExecutor.java:166)
    at org.codehaus.mojo.exec.ExecMojo.executeCommandLine (ExecMojo.java:804)
    at org.codehaus.mojo.exec.ExecMojo.executeCommandLine (ExecMojo.java:751)
    at org.codehaus.mojo.exec.ExecMojo.execute (ExecMojo.java:313)
    at org.apache.maven.plugin.DefaultBuildPluginManager.executeMojo (DefaultBuildPluginManager.java:137)
    at org.apache.maven.lifecycle.internal.MojoExecutor.doExecute2 (MojoExecutor.java:370)
    at org.apache.maven.lifecycle.internal.MojoExecutor.doExecute (MojoExecutor.java:351)
    at org.apache.maven.lifecycle.internal.MojoExecutor.execute (MojoExecutor.java:215)
    at org.apache.maven.lifecycle.internal.MojoExecutor.execute (MojoExecutor.java:171)
    at org.apache.maven.lifecycle.internal.MojoExecutor.execute (MojoExecutor.java:163)
    at org.apache.maven.lifecycle.internal.LifecycleModuleBuilder.buildProject (LifecycleModuleBuilder.java:117)
    at org.apache.maven.lifecycle.internal.LifecycleModuleBuilder.buildProject (LifecycleModuleBuilder.java:81)
    at org.apache.maven.lifecycle.internal.builder.singlethreaded.SingleThreadedBuilder.build (SingleThreadedBuilder.java:56)
    at org.apache.maven.lifecycle.internal.LifecycleStarter.execute (LifecycleStarter.java:128)
    at org.apache.maven.DefaultMaven.doExecute (DefaultMaven.java:294)
    at org.apache.maven.DefaultMaven.doExecute (DefaultMaven.java:192)
    at org.apache.maven.DefaultMaven.execute (DefaultMaven.java:105)
    at org.apache.maven.cli.MavenCli.execute (MavenCli.java:960)
    at org.apache.maven.cli.MavenCli.doMain (MavenCli.java:293)
    at org.apache.maven.cli.MavenCli.main (MavenCli.java:196)
    at jdk.internal.reflect.DirectMethodHandleAccessor.invoke (DirectMethodHandleAccessor.java:104)
    at java.lang.reflect.Method.invoke (Method.java:577)
    at org.codehaus.plexus.classworlds.launcher.Launcher.launchEnhanced (Launcher.java:282)
    at org.codehaus.plexus.classworlds.launcher.Launcher.launch (Launcher.java:225)
    at org.codehaus.plexus.classworlds.launcher.Launcher.mainWithExitCode (Launcher.java:406)
    at org.codehaus.plexus.classworlds.launcher.Launcher.main (Launcher.java:347)
Caused by: java.io.IOException: error=2, No such file or directory

[INFO] ------------------------------------------------------------------------
[INFO] Reactor Summary for Apache ZooKeeper 3.9.0-SNAPSHOT:
[INFO]
[INFO] Apache ZooKeeper ................................... SUCCESS [  3.395 s]
[INFO] Apache ZooKeeper - Documentation ................... SUCCESS [  1.400 s]
[INFO] Apache ZooKeeper - Jute ............................ SUCCESS [ 10.766 s]
[INFO] Apache ZooKeeper - Server .......................... SUCCESS [ 25.990 s]
[INFO] Apache ZooKeeper - Metrics Providers ............... SUCCESS [  0.303 s]
[INFO] Apache ZooKeeper - Prometheus.io Metrics Provider .. SUCCESS [  2.413 s]
[INFO] Apache ZooKeeper - Client .......................... SUCCESS [  0.214 s]
[INFO] Apache ZooKeeper - Client - C ...................... FAILURE [  0.174 s]
[INFO] Apache ZooKeeper - Recipes ......................... SKIPPED
[INFO] Apache ZooKeeper - Recipes - Election .............. SKIPPED
[INFO] Apache ZooKeeper - Recipes - Lock .................. SKIPPED
[INFO] Apache ZooKeeper - Recipes - Queue ................. SKIPPED
[INFO] Apache ZooKeeper - Assembly ........................ SKIPPED
[INFO] Apache ZooKeeper - Compatibility Tests ............. SKIPPED
[INFO] Apache ZooKeeper - Compatibility Tests - Curator ... SKIPPED
[INFO] Apache ZooKeeper - Tests ........................... SKIPPED
[INFO] Apache ZooKeeper - Contrib ......................... SKIPPED
[INFO] Apache ZooKeeper - Contrib - Fatjar ................ SKIPPED
[INFO] Apache ZooKeeper - Contrib - Loggraph .............. SKIPPED
[INFO] Apache ZooKeeper - Contrib - Rest .................. SKIPPED
[INFO] Apache ZooKeeper - Contrib - ZooInspector .......... SKIPPED
[INFO] ------------------------------------------------------------------------
[INFO] BUILD FAILURE
[INFO] ------------------------------------------------------------------------
[INFO] Total time:  44.900 s
[INFO] Finished at: 2022-08-19T10:59:11-04:00
[INFO] ------------------------------------------------------------------------
[ERROR] Failed to execute goal org.codehaus.mojo:exec-maven-plugin:1.6.0:exec (autoreconf) on project zookeeper-client-c: Command execution failed.: Cannot run program "autoreconf" (in direc
tory "/Users/deepan/workspace/github/zookeeper/zookeeper-client/zookeeper-client-c"): error=2, No such file or directory -> [Help 1]
```

Turns out that I didn't have the necessary build tools for the c-client installed. Installed **autoconf**, **automake** through homebrew.

```console
[INFO] --- exec-maven-plugin:1.6.0:exec (autoreconf) @ zookeeper-client-c ---
aclocal: warning: couldn't open directory '/usr/share/aclocal': No such file or directory
acinclude.m4:315: warning: macro 'AM_PATH_CPPUNIT' not found in library
configure.ac:38: error: Missing AM_PATH_CPPUNIT or PKG_CHECK_MODULES m4 macro.
acinclude.m4:317: CHECK_CPPUNIT is expanded from...
configure.ac:38: the top level
autom4te: error: /usr/local/opt/m4/bin/m4 failed with exit status: 1
aclocal: error: /usr/local/Cellar/autoconf/2.71/bin/autom4te failed with exit status: 1
autoreconf: error: aclocal failed with exit status: 1
[ERROR] Command execution failed.
org.apache.commons.exec.ExecuteException: Process exited with an error: 1 (Exit value: 1)
    at org.apache.commons.exec.DefaultExecutor.executeInternal (DefaultExecutor.java:404)
    at org.apache.commons.exec.DefaultExecutor.execute (DefaultExecutor.java:166)
    at org.codehaus.mojo.exec.ExecMojo.executeCommandLine (ExecMojo.java:804)
    at org.codehaus.mojo.exec.ExecMojo.executeCommandLine (ExecMojo.java:751)
    at org.codehaus.mojo.exec.ExecMojo.execute (ExecMojo.java:313)
    at org.apache.maven.plugin.DefaultBuildPluginManager.executeMojo (DefaultBuildPluginManager.java:137)
    at org.apache.maven.lifecycle.internal.MojoExecutor.doExecute2 (MojoExecutor.java:370)
    at org.apache.maven.lifecycle.internal.MojoExecutor.doExecute (MojoExecutor.java:351)
    at org.apache.maven.lifecycle.internal.MojoExecutor.execute (MojoExecutor.java:215)
    at org.apache.maven.lifecycle.internal.MojoExecutor.execute (MojoExecutor.java:171)
    at org.apache.maven.lifecycle.internal.MojoExecutor.execute (MojoExecutor.java:163)
    at org.apache.maven.lifecycle.internal.LifecycleModuleBuilder.buildProject (LifecycleModuleBuilder.java:117)
    at org.apache.maven.lifecycle.internal.LifecycleModuleBuilder.buildProject (LifecycleModuleBuilder.java:81)
    at org.apache.maven.lifecycle.internal.builder.singlethreaded.SingleThreadedBuilder.build (SingleThreadedBuilder.java:56)
    at org.apache.maven.lifecycle.internal.LifecycleStarter.execute (LifecycleStarter.java:128)
    at org.apache.maven.DefaultMaven.doExecute (DefaultMaven.java:294)
    at org.apache.maven.DefaultMaven.doExecute (DefaultMaven.java:192)
    at org.apache.maven.DefaultMaven.execute (DefaultMaven.java:105)
    at org.apache.maven.cli.MavenCli.execute (MavenCli.java:960)
    at org.apache.maven.cli.MavenCli.doMain (MavenCli.java:293)
    at org.apache.maven.cli.MavenCli.main (MavenCli.java:196)
    at jdk.internal.reflect.DirectMethodHandleAccessor.invoke (DirectMethodHandleAccessor.java:104)
    at java.lang.reflect.Method.invoke (Method.java:577)
    at org.codehaus.plexus.classworlds.launcher.Launcher.launchEnhanced (Launcher.java:282)
    at org.codehaus.plexus.classworlds.launcher.Launcher.launch (Launcher.java:225)
    at org.codehaus.plexus.classworlds.launcher.Launcher.mainWithExitCode (Launcher.java:406)
    at org.codehaus.plexus.classworlds.launcher.Launcher.main (Launcher.java:347)
```

- Found the same issue in the discussion threads of [ZOOKEEPER-3879](https://issues.apache.org/jira/browse/ZOOKEEPER-3879?jql=project%20%3D%20ZOOKEEPER%20AND%20status%20%3D%20Open%20AND%20component%20%3D%20%22c%20client%22) and in this [gitter talk](https://gitter.im/apache/apache-zookeeper?at=5d6e2b041e31671227fcc24a).
- Installed cppunit `brew install cppunit`, then tried `mvn clean install -P full-build -DskipTests`. That went through good (However, the same didn't work on another mac with the same configuration :()

```console
[INFO] ------------------------------------------------------------------------
[INFO] Reactor Summary for Apache ZooKeeper 3.9.0-SNAPSHOT:
[INFO]
[INFO] Apache ZooKeeper ................................... SUCCESS [  4.203 s]
[INFO] Apache ZooKeeper - Documentation ................... SUCCESS [  2.410 s]
[INFO] Apache ZooKeeper - Jute ............................ SUCCESS [ 26.359 s]
[INFO] Apache ZooKeeper - Server .......................... SUCCESS [ 41.403 s]
[INFO] Apache ZooKeeper - Metrics Providers ............... SUCCESS [  0.422 s]
[INFO] Apache ZooKeeper - Prometheus.io Metrics Provider .. SUCCESS [  3.681 s]
[INFO] Apache ZooKeeper - Client .......................... SUCCESS [  0.375 s]
[INFO] Apache ZooKeeper - Client - C ...................... SUCCESS [ 52.040 s]
[INFO] Apache ZooKeeper - Recipes ......................... SUCCESS [  0.515 s]
[INFO] Apache ZooKeeper - Recipes - Election .............. SUCCESS [  1.466 s]
[INFO] Apache ZooKeeper - Recipes - Lock .................. SUCCESS [  1.178 s]
[INFO] Apache ZooKeeper - Recipes - Queue ................. SUCCESS [  0.720 s]
[INFO] Apache ZooKeeper - Assembly ........................ SUCCESS [  6.525 s]
[INFO] Apache ZooKeeper - Compatibility Tests ............. SUCCESS [  0.286 s]
[INFO] Apache ZooKeeper - Compatibility Tests - Curator ... SUCCESS [  1.037 s]
[INFO] Apache ZooKeeper - Tests ........................... SUCCESS [  5.884 s]
[INFO] Apache ZooKeeper - Contrib ......................... SUCCESS [  0.290 s]
[INFO] Apache ZooKeeper - Contrib - Fatjar ................ SUCCESS [  5.291 s]
[INFO] Apache ZooKeeper - Contrib - Loggraph .............. SUCCESS [  5.346 s]
[INFO] Apache ZooKeeper - Contrib - Rest .................. SUCCESS [  4.711 s]
[INFO] Apache ZooKeeper - Contrib - ZooInspector .......... SUCCESS [  9.440 s]
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
```

- The [docker method](https://github.com/apache/zookeeper/blob/master/dev/docker/run.sh) worked good to build the repo within a contained based on maven:3.6.3-jdk-8

To summarize, the following steps worked good on macOS Monterey to build the overall zookeeper source, including the c-client.

- Installed [homebrew](https://brew.sh)
- Installed **mvn autoconf automake cppunit** using **brew**
- Built the source using  **mvn clean install -P full-build -DskipTests**

To build just the c-client,

```bash
cd zookeeper-client/zookeeper-client-c/
ACLOCAL="aclocal -I /usr/local/share/aclocal" autoreconf -if
./configure --enable-debug #enabled debug symbols just in case 
make 
make install #to install the libraries (libzookeeper_st, libzookeeper_mt) and binaries (cli_st, cli_mt, load_gen) into /usr/local/
```
