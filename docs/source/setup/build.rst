************
生成容器镜像
************

背景介绍
---------

COD 项目从架构之初，就面向云端设计，部署时首选支持容器化发布。所以基于源码构建镜像是关键步骤。
我们推荐使用 s2i(source to image) 工具直接从代码生成镜像，更多知识请 `查看官方 <https://github.com/openshift/source-to-image/>`_

.. note:: 镜像是由基础环境和代码构成的，这就是 s2i 的设计哲学。一种开发语言，对应特有运行环境。每次打包只是业务代码改变而已。


安装 S2I 命令
--------------

**For Mac**

可以按照 Linux 的安装方法 (使用 darwin-amd64 链接)，或者直接使用 ``homebrew``

``$ brew install source-to-image``

**For Linux**

到 `releases <https://github.com/openshift/source-to-image/releases/latest/>`_ 页面下载对应版本的 tar 包

.. code-block:: shell

    # 解压缩
    $ tar -xvf release.tar.gz
    # 拷贝可执行文件到 $PATH
    cp /path/to/s2i /usr/local/bin

.. note:: 更多环境安装请查阅 S2I `官方仓库 <https://github.com/openshift/source-to-image/>`_


定制 S2I 模板
--------------

s2i 模板，就是我们上文所说的运行环境。社区主流的 `python模板 <https://github.com/sclorg/s2i-python-container>`_ 已支持大部分场景。
但我们仍然定制了自己的模板，兼容社区模板的同时，使用更加灵活和高效。

.. code-block:: shell

    # 克隆开源仓库
    git clone https://github.com/pyfs/s2i-python-container.git
    # 执行编译命令，如果需要请编辑 Makefile 修改镜像仓库地址
    cd s2i-python-container
    make first && make build && make push

.. note:: pyfs/s2i-python-container 基于 centos7 镜像，可以灵活指定 python 版本，安装系统级依赖和 pip 依赖。模板镜像采用 dockerfile 多阶段构建,方便快捷.


打包 COD 代码
-------------

``!!! 假设上述步骤打包的 S2I 模板镜像为: s2i-python-container:latest``

按如下步骤操作:

.. code-block:: shell

    # 克隆 COD 源码
    git clone https://github.com/pyfs/Cod.git
    cd Cod
    # s2i build
    s2i build . s2i-python-container:latest cod:latest