_以下内容是AI翻译的，不保证准确和可读_

# 委托自动分类

本项目与 [ALAS](https://github.com/LmeSzinc/AzurLaneAutoScript) 配合使用。
ALAS 能告诉你获得了什么委托奖励，但数千个委托的记录可能会让人感到烦恼。
我写这个项目是为了让分类过程（可能只有我会做）变得更容易。

## 使用方法
### 数据分析
1. 将图片放在任意文件夹中，main.py 会询问具体位置。默认文件夹是 `commission`，因为这是 ALAS 存放所有图片的地方。
2. 运行 `main.py`。
    - 确保你的硬盘有足够的空间！`main.py` 会将所有图片**复制**到输入文件夹，因此会暂时占用你的磁盘空间。
3. <del>查看 [说明](https://github.com/LmeSzinc/AzurLaneAutoScript/wiki/item_statistics_en) 了解如何使用 ALAS 提供的官方统计工具。</del><br>只需将 `tools/item_statistics.py` 复制到你的 `AzurLaneAutoScript` 文件夹。然后使用 `./toolkit/python item_statistics.py` 运行它。
    - **重要**：为了使临时模板正确，你需要暂时修改 `module\statistics\get_items.py`。将最后几行改为：
    ```
    im_bgr = cv2.cvtColor(im, cv2.COLOR_RGB2BGR)
    cv2.imwrite(os.path.join(folder, f'{name}.png'), im_bgr)
    ```
    否则输出图片中会出现奇怪的 BGR 颜色。完成后记得改回来。
    - 如果你使用本仓库的默认设置，该脚本中的 `FOLDER` 将是 `./Result`。
    - 你不需要进行第一次运行，因为我们会用 `data_proc.py` 来处理。顺便说一下，我的资源应该比官方的更稳健。
    - 虽然第一次运行不是必需的，但我仍然希望你能运行它，<span style="color:red">因为出现在你文件夹中的资源可以让这个仓库变得更强大。</span>不过我不会去提交给 ALAS，因为那太可怕了 QWQ。
    - 如果你看到类似 `Warning: not drop_image` 的提示，这是正常的，因为 ALAS 有时会因点击太快而截图到主页面，或者单纯是因为没有掉落物品。这个问题可能让最终的结果偏小，但是幅度不大并且主要集中在部件和魔方委托中，因为有时候有掉落但没有截图。
4. 运行 `data_proc.py`。它会指导你填写 ALAS 未能识别的资源。
5. 享受你的统计结果吧！现在你可以炫耀一下了！

### 注意事项
你可能会注意到 ALAS 的资源颜色很奇怪。这是因为 LME 在使用 cv2 时出现了一个错误，使用 `tools.py` 中的 `rotate_channels()` 可以修正这个颜色问题。

### 独立脚本
每个脚本都可以独立运行，你可以直接运行它们或构建自己的处理链。`tools.py` 中有一些预定义的实用工具，在进行文件系统操作时可能会用到。

将文件放入 TODO 文件夹（**阅读 config.yaml 以查看应该放入哪个子文件夹**）并运行具有所需效果的脚本。在弹出的文件夹中查看结果。

如果有时间的话，我会考虑写一个 `requirements.txt`。

## 项目内容

ALAS 会将它一次检查的所有委托堆叠在一起，这有点烦人。
所以我写了一个脚本来将它们分成单独的堆叠。

此外，ALAS 不检查委托是否大成功，所以我也添加了这个功能。

以下是我还想做的事情：
- 添加一种通过检查奖励图片来确定委托类型的方法
- 移除 ALAS 有时错误放入截图的主页面图片