# 胎教故事集

![胎教故事 Logo](assets/logo.png)

温暖的胎教朗读故事站。

- 在线：https://story.giscafer.com（GitHub Pages）
- 源码：[github.com/giscafer/prenatal-story](https://github.com/giscafer/prenatal-story)
- 关于：[giscafer.com](https://giscafer.com)

## 功能

- 原创中文胎教故事（文章式排版）
- 按分类浏览：自然与四季 / 动物朋友 / 家人的爱 / 勇气与善良 / 中国传说改写 / 睡前安抚
- 首页可按标题、正文、分类筛选
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
