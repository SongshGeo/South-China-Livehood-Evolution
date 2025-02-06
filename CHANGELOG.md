# Changelog

## [0.7.0](https://github.com/SongshGeo/South-China-Livehood-Evolution/compare/v0.6.2...v0.7.0) (2025-02-06)


### Features

* **agents:** :sparkles: compete whenever put on a cell with farmer ([a495eda](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/a495eda0daad85fe0eefbdabcdde15e04cc6152f))
* **agents:** :sparkles: hunter complexity based on lim_h data ([54da210](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/54da210f293c09a2ac2d9f97dc2861dd807cf7ee))
* **agents:** :sparkles: init all necessary attributes of agents ([6619fea](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/6619fea8500d20aa174b04d0b9a87ec3eea736d3))
* **agents:** :sparkles: inspect conversions between different breeds ([eddd81c](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/eddd81cd747d49513e61edf9cd5f48f4dbe6d822))
* **agents:** :sparkles: logic of diffuse ([1a0c1c4](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/1a0c1c4c1ae2a7b106ad64e16eb20135fc5c6c5a))
* **agents:** :sparkles: population lim_h and lim_g ([41c8535](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/41c8535786df8f6c03ac1167ebb091879535bb4f))
* **agents:** :sparkles: report core attributes of an agent ([be7b43d](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/be7b43d7fc35712b3bd287c043819517ca6bd21e))
* **agents:** :sparkles: rice farmer cannot appear before converting tick ([15442ea](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/15442ea5ed51b2139f6a304cfac1372b56914c66))
* **agents:** :sparkles: 农民人数超过100后就不再转化 ([1de4528](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/1de4528a6a671dc2505970d1e1b1abf2f094d74b))
* **agents:** :sparkles: 农民现在每个时间步会损失一定人数 ([f7be0e4](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/f7be0e48cb2deec589620e5f22ec8afab3c58ed9))
* **agents:** :sparkles: 添加种植水稻的农民主体 ([8a12680](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/8a126802394ae3e5488f81ac4b20a832f2037874))
* **analysis:** :art: 绘制展示人口和族群数量随时间变化的堆积图 ([222ddd7](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/222ddd75e244fde013e93dafc60f2aaed1f2d433))
* **analysis:** :sparkles: added a hist plot of breakpoints ([64cfb03](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/64cfb0349c95115fb7c2f782d419666a40a29d27))
* **analysis:** :sparkles: combine different exp results and plot dynamic line ([0e2a946](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/0e2a9465c51a0a89c0cb40a2973804f8829ac612))
* **analysis:** :sparkles: 增加了一个可视化的基本模型 ([3598cf3](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/3598cf342a20e72a48511978dbfe1200c1584667))
* **analysis:** :sparkles: 增加水稻农民的绘图 ([c823b69](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/c823b6974ea097befc6378b74cfca0c277e715ba))
* **analysis:** :sparkles: 现在可以检测人数哪一年发生了变化 ([a35f4fc](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/a35f4fcf67d82cba362b42e730ac737fdc4f6a48))
* **analysis:** :sparkles: 绘制聚合多个实验结果的分析图 ([227301d](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/227301d6cd5231c2e5c3a2e23c37b752886d29ca))
* **analysis:** :sparkles: 记录断点前后的增长率 ([4c57ee4](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/4c57ee46ad632e43439784d26c4e190b8260a7b9))
* **analysis:** :wrench: 使用 config 配置文件来控制可视化参数 ([8517f44](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/8517f449a2237b8c7be92ca8b3a50c724b22cd73))
* **analysis:** :wrench: 增加可视化配置范围，初始值从默认配置读取 ([7b4aadd](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/7b4aadd2985e2bc36ce423469d8434281b8b6971))
* **docs:** :memo: 在demo.ipynb里展示有多少适合的斑块 ([ed47e99](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/ed47e9954e277173c88259259685b618e64adb3b))
* **exp:** :art: 制作热力图来反映随两个参数变化的某个值 ([8778526](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/87785265866e191c604626e4ae1e8e6d1db49ad4))
* **exp:** :sparkles: multiple run and plotting supports ([0fee4ff](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/0fee4ff28c920c3c26d4f77c365a1617aeafb094))
* **exp:** :sparkles: multiple run support ([e23be8b](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/e23be8b7055456d6388781f8dafd0e2a4071e592))
* **modules:** :sparkles: farmers choose location based on prob of arable level ([6019d5c](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/6019d5cf6f228ac4bd6db95f803ebb6bd7b5b1d6))
* **modules:** :sparkles: plot spatial heatmap ([d0f0404](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/d0f0404c1c63dc050c13a49dd619dc3ebfbbb2c7))
* **modules:** :sparkles: users can adjust possion expect ([d1e16d4](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/d1e16d421673d984d03e8ab7ad3df67ec9493aef))
* **modules:** :sparkles: 初始添加狩猎采集者，单个agent人数范围设置在【0,35】的区间内 ([3d2b378](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/3d2b37801cb9d17d15eb1e92ae3d24095e4df1f6))
* **modules:** :sparkles: 将主体的基本能力框架搭建好 ([f4d8ebc](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/f4d8ebcf463ef424ac211b03c7e4a9fdf75c2ab6))
* **modules:** :sparkles: 狩猎采集者主体之间现在融合而不是竞争 ([daed537](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/daed5379cf921849b163a511860b0c140c2a0c19))
* **nature:** :sparkles: add rice farmers each step ([ce75893](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/ce75893ee3175bb377379245725041d409487a32))
* **nature:** :sparkles: adding new farmers ([5a7ecdb](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/5a7ecdb8e65b203b693b07372feeb52370399e7c))
* **nature:** :sparkles: adding some init hunters when setup ([3d47078](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/3d47078454408b7a777d21f05dabaaba4c910bab))
* **nature:** :sparkles: init env successfully ([41fe39d](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/41fe39d52fc7c5bb52362475073226c5210e47b6))
* **nature:** :sparkles: initial hunter agents setup ([468db75](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/468db75dc50644cc5e4b01d26c959672e12649db))
* **nature:** :sparkles: using lim_h dataset ([83bf567](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/83bf5672f7837e3f23f099db1219b73909954802))
* **project:** :sparkles: run succesfully ([d049894](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/d049894d09d4bac2355319176bd23da3d261da2b))
* **project:** :sparkles: 实现局部小模型的可视化 ([d90104c](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/d90104c1359eda108b17d9f7b305f90169144537))
* **project:** :sparkles: 新增记录农民狩猎采集者群体数量的折线图，所有的画图功能迁移到ModelViz类 ([f22410a](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/f22410ad7ffcf0ab5d2273b72253c0e741ec7f02))


### Bug Fixes

* **agents:** :bug: compete with all kind of agents ([27102c4](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/27102c47f85729b1be8c2ea39914e11ce3baa2f6))
* **agents:** :bug: diffuse: if size &lt; min_group, no diffuse ([3d163a8](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/3d163a8913f55c5d23741f289cd025f5643fdcfb))
* **agents:** :bug: fix farmer not growth problem ([896d006](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/896d0066d1dc29cad76a3dcb0e7a820c714c3f7c))
* **agents:** :bug: fixed competeting without rice farmer bug ([95b2649](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/95b2649ecb5067f16c8161ae20d63cef9af2e468))
* **agents:** :bug: hunter's h_lim as max_size ([f870d07](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/f870d071fabc0001ecd9d3961098b80c6b2ee03f))
* **agents:** :bug: hunters set max size correctly as lim_h now ([9e141fb](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/9e141fbfb70bfcc1ec822b3c588f93327c1fcb3a))
* **agents:** :bug: size settings problem ([eb0ce9a](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/eb0ce9a29a9eff70143c160ccec1a98b9e0d7657))
* **agents:** :bug: 修正为外部农民进入时间的调整 ([f6b9263](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/f6b926327e69e737efa501c4acdf7ddc823de48d))
* **agents:** :white_check_mark: diffusion died pass test ([e15bf0d](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/e15bf0d86bccada3a4c04647fabb5d76f58dfd30))
* **analysis:** :bug: fix three types of agent plotting ([e786256](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/e78625677c916605526440905cb7bd070b649417))
* **analysis:** :bug: plot rice farmers' heatmap correctly ([2885581](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/2885581de6bb771a236f885c356eda6e20fe96ed))
* **analysis:** :bug: 不再绘制核密度图 ([84e44f2](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/84e44f2136e4b863d9be48921a970fea4da9992b))
* **analysis:** :bug: 修复了初始主体全消失的问题 ([590718e](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/590718e387dad657dcfdc2c1e28444015dc307cf))
* **analysis:** :bug: 修复了增长率计算的公式，现在使用两边直线的斜率 ([b003745](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/b0037456e5023e713cf2ffa6cbd100a0358e50f9))
* **analysis:** :bug: 修正 histplot 两张图一样 ([b875b14](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/b875b1491277a7b7c922a6a025d6706b251f1a40))
* **analysis:** :bug: 修正分布直方图的绘制 ([91eed72](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/91eed722cb45b52f5cef296b37ec968293f768dd))
* **analysis:** :bug: 折线图改回用主体人数，同时能够修改断点数量 ([caddc9c](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/caddc9cfe58305a9cba2629a272f8d2896897776))
* **analysis:** :bug: 现在使用主体的数量来识别断点，并增加选择哪一个来识别的功能 ([2a9db23](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/2a9db23852b9672804bfab3557afd83d58670373))
* **docs:** :memo: fix mkdocs-strings paths ([efee334](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/efee3346e9e9f2abbb1315fa2b826395c95e1bc6))
* **modules:** :ambulance: model run failed in compete because of None cell ([174908e](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/174908e9fd4885404ba89a69bb9838dfcd8bcc80))
* **modules:** :bug: adding farmers on existing cells problem ([63d3808](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/63d3808e1a221d889f422ad92ba8602836e876a3))
* **modules:** :bug: fixing convert None cell problem ([914e620](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/914e620e9537da17f658a742e35c4ef3aa372041))
* **modules:** :zap: random uniform to randint ([5068cf4](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/5068cf4fed0b79821ac853ec09907919e5d12acb))
* **nature:** :bug: fixing arable problem and test the nature ([8b07b3d](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/8b07b3db3143c4094f6024b9ac339a8689656fb6))
* **nature:** :bug: 修复`add_hunters`方法的bug ([8198b5b](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/8198b5b0db57e74fdb275e8d24828083bb1b17ce))
* **nature:** :bug: 修复了初始狩猎采集人口量不能调整的bug ([ed65c01](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/ed65c01cb16d30c485405742ca788547cf584f47))
* **nature:** :bug: 修复了在服务器上不能切换root的bug ([9a7b1d5](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/9a7b1d53089a467d4c349406bf036bdae49f6de9))
* **project:** :ambulance: test failed setup ([5ca2e45](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/5ca2e45abf14712de830ed76b0e81c9bf9805dc2))
* **project:** :bug: population growth correctly now ([4ab8fd3](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/4ab8fd3c3c686dcae3b96c86d631c2f7b292de6c))
* **project:** :fire: remove redundant paprameter and upload data ([e27a278](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/e27a2786824f9dd01e4b39027f157b2a47cc993c))
* **project:** :package: update to v0.2.0, rename package ([fadcef0](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/fadcef04e7b6b252aa75848081fcbe4193bcf678))
* **project:** :rotating_light: fixing random int deprecation warning ([2e74671](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/2e7467141c5706ef0f28b82be04930d94f204220))
* **project:** :see_no_evil: remove data folder because of failure of uploading ([2d7ca61](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/2d7ca61c06c0b9b22e5fe8fe6fdd44d3cd6d28e7))


### Performance Improvements

* **analysis:** :art: 分开不同的主体类别来绘制断点 ([c7290d4](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/c7290d4c2b52f93d45868a6580cc2e12910bf48b))


### Documentation

* **adding hunter api:** docs(adding hunter api):  ([83e4df4](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/83e4df4643be85579e1596e2ccd251c38737b500))
* **docs:** :memo: adding farmer api ([23603ef](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/23603effa7799d4c8b9667a824bc11cf03826a76))
* **docs:** :memo: describe modeling workflow ([35b1aab](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/35b1aab5dc5223292479b852d71157d2f28d5fde))
* **docs:** :memo: feature requests from Lian Zhang ([cfb2f9c](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/cfb2f9c8f13237c5a63153c666c6e995894b753d))
* **docs:** :memo: 完善项目介绍文档 ([f04ff0d](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/f04ff0d2f4a0160e5032a56edc413ddf458c8578))
* **docs:** :memo: 整理最新的文档 ([71c777b](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/71c777b47e2a625fb60a35bda53cd78b4a468e6e))
* **nature:** :memo: nature documentation ([775e3c9](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/775e3c954669553992e303868c9f542f798c7a32))
* **project:** :bookmark: update changelog for v-0.3.1 ([a3bc366](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/a3bc36660a9aeb5ea1cb50030aa2077084885650))
* **project:** :bookmark: update to version 0.4.2 ([5bef49a](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/5bef49a0b297dbb99615db375a306bcf855f6b4f))
* **project:** :bookmark: v 0.3.2 changelog ([6e6707b](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/6e6707baccf2358a56df6b9f6826fbeb019fd6b6))
* **project:** :bookmark: 更新到0.5.0，适配0.5.x版本的ABSESpy ([6a32653](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/6a3265348c406a4c43a60addde4469b867aaa51c))
* **project:** :bookmark: 更新到0.6.0版本 ([949374b](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/949374b16dc1a807b6ad66f1f18fe389e94c8521))
* **project:** :memo: adding change log for v-0.4.1 ([ceb8766](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/ceb87668122fa9e2d63cabba0ab67d1a35656981))
* **project:** :memo: setup docs framework ([78dd73e](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/78dd73ebaa20385ed1313cf00b0eb9c5c26efd1c))
* **project:** :memo: some idea notes from meeting ([8896eea](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/8896eea69916271a4a1020ad82b83ce5b2ac1bc7))
* **project:** :memo: update changelog docs ([3ae7722](https://github.com/SongshGeo/South-China-Livehood-Evolution/commit/3ae7722f97d1cc87e3a6daf397028d1306ae3ca4))

<a id='changelog-0.6.2'></a>
## 0.6.2 — 2024-10-08

## New Features

- [x] #feat✨ 绘制两组参数对应结果的热力图

## Documentation changes

- [x] #docs📄 根据最新的模型重写文档架构

## Fixed bugs

- [x] #bug🐛 修复了不能改变初始狩猎采集者数量的问题
- [x] #bug🐛 折线图改回主体人数

## Refactoring

- [x] #refactor♻ 采用ABSESpy 0.6.9 版本的框架
- [x] 将源代码分组以便于管理

## New Features

- [x] #feat✨ 记录断点前后的增长率
- [x] #feat✨ 放宽了依赖的版本要求

<a id='changelog-0.6.1'></a>
## 0.6.1 — 2024-07-02

## Fixed bugs

- [x] #bug🐛 修复了在服务器上不能切换root的bug

<a id='changelog-0.6.0'></a>
## 0.6.0 — 2024-05-12

## Performance improvements

- [x] #zap⚡️ 可以并行运算，所以重复实验的速度提升了很多

## New Features

- [x] #feat✨ 现在可以根据多组实验结果画出带误差范围的变化曲线
- [x] #feat✨ 现在可以绘制不同重复实验后，各类主体数量的断点分布
- [x] #feat✨ 绘制对数变化后的主体数量分布热力图

## Fixed bugs

- [x] #bug🐛 修复了水体范围不正确的 bug

## Refactoring

- [x] #refactor♻️ 适配0.6.x版本的`ABSESpy`框架
- [x] #refactor♻️ 删除了新版本下过去多余的代码

<a id='changelog-0.5.0'></a>
## 0.5.0 — 2024-03-27

## Fixed bugs

- [x] #bug🐛 修复了竞争中失败者可能意外损失的 bug

## Refactoring

- [x] #refactor♻️ 适配到最近的 ABSESpy 版本 0.5.x

<a id='changelog-0.4.2'></a>
## 0.4.2 — 2024-03-20

## Fixed bugs

- [x] #bug🐛 修正为外部农民进入时间的调整

<a id='changelog-0.4.1'></a>
## 0.4.1 — 2024-03-10

## New Features

- [x] #feat✨ 现在可以检测人数哪一年发生了变化
- [x] #feat✨ 水稻农民可以设定为某个时间之前不出现（参数 `farmer.tick`）
- [x] #feat✨ 农民现在每个时间步会以一定概率按比例损失人数 （参数 `farmer.loss`）

## Documentation changes

- [x] #docs📄 在`demo.ipynb`里展示有多少适合的斑块

<a id='changelog-0.4.0'></a>
## 0.4.0 — 2024-02-04

## Fixed bugs

- [x] #bug🐛 fix(project): :rotating_light: fixing random int deprecation warning
- [x] #bug🐛 修改 mkdocs vercel 部署文档的 CI

## New Features

- [x] #feat✨ 绘制展示人口和族群数量随时间变化的堆积图
- [x] #feat✨ feat(analysis): :sparkles: 绘制聚合多个实验结果的分析图

<a id='changelog-0.3.2'></a>
## 0.3.2 — 2024-01-12

## New Features

- [x] #feat✨ inspect conversions between different breeds

## Fixed bugs

- [x] #bug🐛 fixed competing without rice farmer bug
- [x] #bug🐛 plot rice farmers' heatmap correctly

## Refactoring

- [x]  #refactor♻️ improve code format by sourcery

<a id='changelog-0.3.1'></a>
## 0.3.1 — 2024-01-11

## Performance improvements

- [x]  #zap⚡️ upgrade `seaborn` to mute the future warnings from `pandas`

## Fixed bugs

- [x]  #bug🐛 Fixing plotting for rice farmer

## New Features

- [x]  #feat✨ Add rice farmers in each step

## Documentation changes

- [x] #docs📄 update paths for `mkdocs-strings`

<a id='changelog-0.3.0'></a>
## 0.3.0 — 2024-01-05

## New Features

- [x] #feat✨ 增加种植水稻的农民

## Refactoring

- [x] #refactor♻️ 删除坡向的影响
- [x] #refactor♻️ 把适宜度改成内部代码而不是数据
- [x] #refactor♻️ 水稻和普通农民的人口上限改成参数

<a id='changelog-0.2.3'></a>
## 0.2.3 — 2023-12-11

## Fixed bugs

- [x] #bug🐛 修改两个`histplot`图一样

<a id='changelog-0.2.2'></a>
## 0.2.2 — 2023-12-11

- [x] #bug🐛 `histplot` 分布直方图修正

<a id='changelog-0.2.1'></a>
## 0.2.1 — 2023-12-09

## New Features

- [x] #feat✨ 两个新的折线图，表示农民和狩猎采集者群体的数量，而不是人数

## Refactoring

- [x] #refactor♻️ 将所有的画图功能转移到 `ModelViz` 类

<a id='changelog-0.2.0'></a>
## 0.2.0 — 2023-12-03

## New Features

- [x] #feat✨ 初始添加狩猎采集者，单个agent人数范围设置在【0,35】的区间内，即仍不存在复杂狩猎采集者
- [x] #feat✨ 农民人数超过100后就不会convert为狩猎采集者
- [x] #feat✨ 批量测试（1）init_hunters （2）convert_prob （3）loss_rate （4）intensified_coefficient

<a id='changelog-0.1.0'></a>
## 0.1.0 — 2023-11-25

## Fixed bugs

- [x] #bug🐛 修复了农民主体出生在已有主体斑块的情况
- [x] #bug🐛 修复了失败的狩猎采集者因为复杂化不会逃跑的情况
- [x] #bug🐛 修复了人口不会自然增长的问题

## New Features

- [x] #feat✨ 使用外部数据作为狩猎采集者的人口承载力上限

- [x] #feat✨ 农民只于可耕种区域定居，并会在搜索范围内优先选择可耕适宜度更高的地块（具体适宜度待细化）；

- [x] #feat✨ 开局设置存在部分狩猎采集者，其群体个数可以按地块数1％-5％来设置，数量在范围内（6-地块上限）随机；

- [x] #feat✨ 生成模拟结果中人群具体分布的热力图
- [x] #feat✨ 汇报每个agent具体的数量、位置等属性

## Documentation changes

- [x] #docs📄 更新文档并发布
- [x] #docs📄 更新版本日志
