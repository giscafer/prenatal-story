# 胎教故事集

![胎教故事 Logo](assets/logo.png)

温暖的胎教朗读故事站。

- 在线：https://story.giscafer.com（GitHub Pages）
- 源码：[github.com/giscafer/prenatal-story](https://github.com/giscafer/prenatal-story)
- 关于：[giscafer.com](https://giscafer.com)

## 功能

- 100 篇原创中文故事与 16 篇世界经典童话的中文精简改写（文章式排版）
- 按分类浏览：世界经典童话 / 自然与四季 / 动物朋友 / 家人的爱 / 勇气与善良 / 中国传说改写 / 睡前安抚
- 首页可按标题、正文、作者、分类及未读 / 已读状态组合筛选；筛选条件保存在 URL，支持直接分享
- 首页和正文首尾都可手动标记已读、撤销；`localStorage` 保存稳定故事 ID，同源标签页同步，无需账号
- 阅读记录仅存当前浏览器，不跨设备或域名同步；清除网站数据后重置。存储被禁用或写入失败时提示仅本次页面有效，记录格式异常时可重新标记
- 正文显示字数与预计朗读时间，按每分钟 180–220 字估算；构建校验正文不超过 900 个中英文及数字字符（按慢速估算不超过 5 分钟），不含导读、提示与来源，实际随语速和停顿变化
- 经典童话逐篇标注作者 / 整理者、原作参考与温和改写范围，非原作全译
- 回到顶部火箭动画
- 移动端友好

## 本地预览

静态站点，打开 `index.html` 或任意静态服务器即可：

```bash
python3 -m http.server 8080 --directory .
```

重新生成页面：

```bash
python3 build.py
```

`stories.json` 保留原有 100 篇，`classics.json` 维护新增经典童话。`build.py` 只生成 HTML，`css/` 与 `js/` 为直接维护的源文件，不会被构建覆盖。故事 ID 一经发布应保持稳定，避免已读记录对应错篇。

运行交付检查（数据、资源、锚点、生成一致性及已读存储行为）：

```bash
python3 tests/check_site.py
node --test tests/reading.test.cjs
```
