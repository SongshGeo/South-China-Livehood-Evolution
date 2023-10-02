# 华南生计演变模型

## 开始使用

### 下载/拉取模型代码

通过`Git`下载并安装该模型的源代码，具体[可参考](https://deepinout.com/git/git-questions/46_git_how_to_setup_and_clone_a_remote_git_repo_on_windows.html)：

```bash
git clone https://github.com/SongshGeo/SC-20230710-SCE.git <your folder name>
```

### 安装Python和包依赖

安装`Python`教程一大把，本模型依赖`python > 3.9`版本。

**选项1**: 除了安装好`python`，还需要根据`requirements.txt`文件里的依赖项，安装所需要的包。具体可以参考[这篇文章](https://zhuanlan.zhihu.com/p/563060853?utm_id=0)。

**选项2**: 我个人更建议使用`poetry`进行管理，借助我写好的`makefile`一键装载模型，[在这里看如何安装poetry](https://python-poetry.org/docs/)。安装好后，在项目所在文件夹里用命令行输入：

```bash
make setup
```

即可自动安装所有的模型依赖包。

### 尝试使用模型

首次使用模型前，强烈建议先使用以下命令测试模型完整性：

```bash
make test
```

这个原理是使用了[`pytest`](https://docs.pytest.org/en/7.4.x/)对程序进行测试。我在开发模型时，已经对每一个方法进行了严格的测试，如果测试不通过，说明该版本模型存在问题，或者用户对代码逻辑进行了更改导致有些测试不通过。如果有代码调试能力，可以在终端使用以下命令查看报告，看看问题出在哪：

```bash
make report
```

- 接下来你可以遵照[快速开始](quick_start.md)调试模型
- 如果想对模型的以下部分进行更改，请参照下面的[方法说明](#方法说明)

## 方法说明

- [模型工作流](api/model.md)
- [农民主体方法](api/farmer.md)
- [狩猎采集者主体方法](api/hunter.md)
- [斑块与环境](api/env.md)
