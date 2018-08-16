## 前端部署

### Node.js安装配置

+ 下面向大家介绍在window和Linux上安装Node.js的方法。本安装教程以Node.js v4.4.3 LTS(长期支持版本)版本为例。

+ Node.js安装包及源码下载地址为：https://nodejs.org/en/download/。
  你可以根据不同平台系统选择你需要的Node.js安装包。
  Node.js 历史版本下载地址：https://nodejs.org/dist/
  注意：Linux上安装Node.js需要安装Python 2.6 或 2.7 ，不建议安装Python 3.0以上版本。

#### Windows安装Node.js

+ 你可以采用以下两种方式来安装：
    + 1、Windows 安装包(.msi)
       32 位安装包下载地址 : https://nodejs.org/dist/v4.4.3/node-v4.4.3-x86.msi
       64 位安装包下载地址 : https://nodejs.org/dist/v4.4.3/node-v4.4.3-x64.msi
       本文实例以 v0.10.26 版本为例，其他版本类似， 安装步骤：
       + 步骤 1 : 双击下载后的安装包 v0.10.26；
       + 步骤 2 : 点击以上的Run(运行)；
       + 步骤 3 : 勾选接受协议选项，点击 next（下一步） 按钮；
       + 步骤 4 : Node.js默认安装目录为 "C:\Program Files\nodejs\" , 你可以修改目录，并点击 next（下一步）；
       + 步骤 5 : 点击树形图标来选择你需要的安装模式 , 然后点击下一步 next（下一步）；
       + 步骤 6 :点击 Install（安装） 开始安装Node.js。你也可以点击 Back（返回）来修改先前的配置。 然后并点击 next（下一步）；
       + 安装过程等待；
       + 点击 Finish（完成）按钮退出安装向导。
       + 检测PATH环境变量是否配置了Node.js，点击开始=》运行=》输入"cmd" => 输入命令"path"，输出如下结果：
       ```
       PATH=C:\oraclexe\app\oracle\product\10.2.0\server\bin;C:\Windows\system32;
       C:\Windows;C:\Windows\System32\Wbem;C:\Windows\System32\WindowsPowerShell\v1.0\;
       c:\python32\python;C:\MinGW\bin;C:\Program Files\GTK2-Runtime\lib;
       C:\Program Files\MySQL\MySQL Server 5.5\bin;C:\Program Files\nodejs\;
       C:\Users\rg\AppData\Roaming\npm
       ```
       我们可以看到环境变量中已经包含了C:\Program Files\nodejs\
       + 检查Node.js版本，点击开始=》运行=》输入"cmd" => 输入命令"node --version"，输出如下结果：
       ```
       v0.10.26
       ```
    + 2、Windows 二进制文件 (.exe)安装
       32 位安装包下载地址 : http://nodejs.org/dist/v0.10.26/node.exe
       64 位安装包下载地址 : http://nodejs.org/dist/v0.10.26/x64/node.exe
       安装步骤：
       + 步骤 1 : 双击下载的安装包 Node.exe；
       + 点击 Run（运行）按钮将出现命令行窗口；
       + 进入 node.exe 所在的目录，点击开始=》运行=》输入"cmd" => 输入命令"node --version"，输出如下结果：
       ```
       v0.10.26
       ```

#### Ubuntu 上安装 Node.js

+ 你可以采用以下两种方式来安装
    + 1、Node.js 源码安装
        + 在 Github 上获取 Node.js 源码：
        ```
        $ sudo git clone https://github.com/nodejs/node.git
        Cloning into 'node'...
        ```
        + 修改目录权限：
        ```
        $ sudo chmod -R 755 node
        ```
        + 使用 ./configure 创建编译文件，并按照：
        ```
        $ cd node
        $ sudo ./configure
        $ sudo make
        $ sudo make install
        ```
        + 查看 node 版本：
        ```
        $ node --version
        v0.10.25
        ```
    + 2、Ubuntu apt-get命令安装
        + 命令格式如下：
        ```
        sudo apt-get install nodejs
        sudo apt-get install npm
        sudo apt-get install nodejs-legacy
        ```

#### CentOS 下安装 Node.js

+ 1、下载源码，你需要在https://nodejs.org/en/download/下载最新的Nodejs版本，本文以v0.10.24为例:
```
cd /usr/local/src/
wget http://nodejs.org/dist/v0.10.24/node-v0.10.24.tar.gz
```
+ 2、解压源码
```
tar zxvf node-v0.10.24.tar.gz
```
+ 3、编译安装
```
cd node-v0.10.24
./configure --prefix=/usr/local/node/0.10.24
make
make install
```
+ 4、 配置NODE_HOME，进入profile编辑环境变量
```
vim /etc/profile
```
&nbsp;&nbsp;&nbsp;&nbsp;设置nodejs环境变量，在 export PATH USER LOGNAME MAIL HOSTNAME HISTSIZE HISTCONTROL 一行的上面添加如下内容:
```
#set for nodejs
export NODE_HOME=/usr/local/node/0.10.24
export PATH=$NODE_HOME/bin:$PATH
```
&nbsp;&nbsp;&nbsp;&nbsp;:wq保存并退出，编译/etc/profile 使配置生效
```
source /etc/profile
```
&nbsp;&nbsp;&nbsp;&nbsp;验证是否安装配置成功
```
node -v
```
&nbsp;&nbsp;&nbsp;&nbsp;输出 v0.10.24 表示配置成功
&nbsp;&nbsp;&nbsp;&nbsp;npm模块安装路径
```
/usr/local/node/0.10.24/lib/node_modules/
```

### NPM 安装依赖

+ NPM是随同NodeJS一起安装的包管理工具，能解决NodeJS代码部署上的很多问题，常见的使用场景有以下几种：
  允许用户从NPM服务器下载别人编写的第三方包到本地使用。
  允许用户从NPM服务器下载并安装别人编写的命令行程序到本地使用。
  允许用户将自己编写的包或命令行程序上传到NPM服务器供别人使用。
  由于新版的nodejs已经集成了npm，所以之前npm也一并安装好了。同样可以通过输入 "npm -v" 来测试是否成功安装。命令如下，出现版本提示表示安装成功:
  ```
  $ npm -v
  2.3.0
  ```

#### 使用 npm 命令安装模块

+ npm 安装 Node.js 模块语法格式如下：
```
$ npm install <Module Name>
 ```
+ npm的包安装分为本地安装（local）、全局安装（global）两种，从敲的命令行来看，差别只是有没有-g而已
    + 本地安装
     1. 将安装包放在 ./node_modules 下（运行 npm 命令时所在的目录），如果没有 node_modules 目录，会在当前执行 npm 命令的目录下生成 node_modules 目录。
     2. 可以通过 require() 来引入本地安装的包。
    + 全局安装
     1. 将安装包放在 /usr/local 下或者你 node 的安装目录。
     2. 可以直接在命令行里使用
```
npm install express          # 本地安装
npm install express -g   # 全局安装
```

#### 使用 package.json
+ package.json 位于模块的目录下，用于定义包的属性。接下来让我们来看下 express 包的 package.json 文件，位于 node_modules/express/package.json 内容：
```
{
  "name": "ics-scanning",
  "version": "1.0.0",
  "description": "工控扫描",
  "main": "app.js",
  "scripts": {
    "test": "http-server -p 12345 -C ."
  },
  "repository": {
    "type": "git",
    "url": "http://10.1.1.45/sec-group/ics_scanning_project.git"
  },
  "keywords": [
    "ICS"
  ],
  "author": "WangAo",
  "license": "ISC",
  "devDependencies": {
    "bower": "^1.8.0",
    "http-server": "^0.10.0"
  },
  "dependencies": {
    "angular": "^1.3.0",
    "angular-bootstrap": "^0.12.2",
    "angular-ui-grid": "^4.0.4",
    "angular-ui-router": "^1.0.3",
    "bootstrap": "^3.3.7",
    "font-awesome": "^4.7.0",
    "install": "^0.10.0",
    "jquery": "^2.1.4"
  }
}

```

+ Package.json 属性说明
  name - 包名。
  version - 包的版本号。
  description - 包的描述。
  homepage - 包的官网 url 。
  author - 包的作者姓名。
  contributors - 包的其他贡献者姓名。
  dependencies - 依赖包列表。如果依赖包没有安装，npm 会自动将依赖包安装在 node_module 目录下。
  repository - 包代码存放的地方的类型，可以是 git 或 svn，git 可在 Github 上。
  main - main 字段是一个模块ID，它是一个指向你程序的主要项目。就是说，如果你包的名字叫 express，然后用户安装它，然后require("express")。
  keywords - 关键字

+ 创建模块
  创建模块，package.json 文件是必不可少的。我们可以使用 NPM 生成 package.json 文件，生成的文件包含了基本的结果。
  ```
  $ npm init
  This utility will walk you through creating a package.json file.
  It only covers the most common items, and tries to guess sensible defaults.

  See `npm help json` for definitive documentation on these fields
  and exactly what they do.

  Use `npm install <pkg> --save` afterwards to install a package and
  save it as a dependency in the package.json file.

  Press ^C at any time to quit.
  name: (node_modules) runoob                   # 模块名
  version: (1.0.0)
  description: Node.js 测试模块(www.runoob.com)  # 描述
  entry point: (index.js)
  test command: make test
  git repository: https://github.com/runoob/runoob.git  # Github 地址
  keywords:
  author:
  license: (ISC)
  About to write to ……/node_modules/package.json:      # 生成地址

  {
    "name": "runoob",
    "version": "1.0.0",
    "description": "Node.js 测试模块(www.runoob.com)",
    ……
  }


  Is this ok? (yes) yes
  ```
  以上的信息，你需要根据你自己的情况输入。在最后输入 "yes" 后会生成 package.json 文件。

+ **安装依赖**
  存在package.json的项目，直接运行"npm install"即可安装依赖。

#### 使用淘宝 NPM 镜像

大家都知道国内直接使用 npm 的官方镜像是非常慢的，这里推荐使用淘宝 NPM 镜像。
淘宝 NPM 镜像是一个完整 npmjs.org 镜像，你可以用此代替官方版本(只读)，同步频率目前为 10分钟 一次以保证尽量与官方服务同步。
你可以使用淘宝定制的 cnpm (gzip 压缩支持) 命令行工具代替默认的 npm:
```
$ npm install -g cnpm --registry=https://registry.npm.taobao.org
```
这样就可以使用 cnpm 命令来安装模块了：