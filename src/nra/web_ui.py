"""Gradio Web UI"""

import os
import json
import gradio as gr

from nra.models.preset_manager import PresetManager
from nra.models.vocabulary import VocabularyLoader


def create_app(data_dir: str = "data"):
    pm = PresetManager(os.path.join(data_dir, "presets.json"))
    vl = VocabularyLoader(data_dir)

    normal_vocab = vl.load(["normal.txt", "normal_special.txt"])
    deepnight_pos_vocab = vl.load(["deepnight_pos.txt"])
    deepnight_neg_vocab = vl.load(["deepnight_neg.txt"])
    all_vocab = vl.load(["normal.txt", "normal_special.txt", "deepnight_pos.txt", "deepnight_neg.txt"])

    # ── 构筑管理 helpers ──

    def get_build_names():
        return [b["name"] for b in pm.builds]

    def get_build_data(name):
        if not name:
            return "", "", "", ""
        for b in pm.builds:
            if b["name"] == name:
                return (
                    "\n".join(b.get("normal_whitelist", [])),
                    "\n".join(b.get("deepnight_whitelist", [])),
                    "\n".join(b.get("deepnight_neg_whitelist", [])),
                    "\n".join(b.get("blacklist", [])),
                )
        return "", "", "", ""

    def save_build(name, normal, deepnight, neg, blacklist):
        if not name:
            return gr.update(), "请先选择构筑"
        for b in pm.builds:
            if b["name"] == name:
                pm.update_build(b["id"],
                    normal_whitelist=[x.strip() for x in normal.split("\n") if x.strip()],
                    deepnight_whitelist=[x.strip() for x in deepnight.split("\n") if x.strip()],
                    deepnight_neg_whitelist=[x.strip() for x in neg.split("\n") if x.strip()],
                    blacklist=[x.strip() for x in blacklist.split("\n") if x.strip()],
                )
                return gr.update(), f"已保存 {name}"
        return gr.update(), "未找到构筑"

    def add_build(name):
        if not name or not name.strip():
            return gr.update(choices=get_build_names()), "名称不能为空"
        pm.create_build(name.strip())
        names = get_build_names()
        return gr.update(choices=names, value=name.strip()), f"已创建 {name.strip()}"

    def delete_build(name):
        if not name:
            return gr.update(choices=get_build_names()), "请先选择构筑"
        for b in pm.builds:
            if b["name"] == name:
                pm.delete_build(b["id"])
                names = get_build_names()
                return gr.update(choices=names, value=names[0] if names else None), f"已删除 {name}"
        return gr.update(), "未找到"

    def search_vocab(query, vocab_type):
        vocab = {"普通": normal_vocab, "深夜正面": deepnight_pos_vocab,
                 "深夜负面": deepnight_neg_vocab, "全部(黑名单)": all_vocab}
        source = vocab.get(vocab_type, normal_vocab)
        if not query:
            return "\n".join(source[:50]) + ("\n..." if len(source) > 50 else "")
        results = [v for v in source if query in v]
        return "\n".join(results) if results else "无匹配"

    def export_builds():
        data = [{k: v for k, v in b.items() if k not in ("id", "common_group_ids")} for b in pm.builds]
        return json.dumps(data, ensure_ascii=False, indent=2)

    def import_builds(text):
        try:
            data = json.loads(text)
            items = data if isinstance(data, list) else [data]
            for item in items:
                name = item.get("name", "导入")
                build = pm.create_build(name)
                pm.update_build(build["id"], **{k: v for k, v in item.items() if k in build and k != "id"})
            return gr.update(choices=get_build_names()), f"已导入 {len(items)} 个构筑"
        except Exception as e:
            return gr.update(), f"导入失败: {e}"

    # ── 构建 UI ──

    with gr.Blocks(title="黑夜君临遗物助手", theme=gr.themes.Soft()) as app:
        gr.Markdown("# 黑夜君临遗物助手")

        with gr.Tabs():
            # ── 自动购买 ──
            with gr.Tab("自动购买"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 匹配设置")
                        shop_match = gr.Dropdown(["双有效", "三有效"], value="双有效", label="匹配模式")
                        gr.Markdown("### 停止条件")
                        shop_no_limit = gr.Checkbox(value=True, label="不限制")
                        shop_threshold = gr.Number(value=10000, label="暗痕阈值", interactive=False)
                        with gr.Row():
                            shop_start = gr.Button("开始", variant="primary")
                            shop_stop = gr.Button("停止", interactive=False)

                        shop_no_limit.change(
                            lambda x: gr.update(interactive=not x),
                            inputs=shop_no_limit, outputs=shop_threshold)

                    with gr.Column(scale=2):
                        gr.Markdown("### 统计")
                        with gr.Row():
                            shop_s1 = gr.Number(value=0, label="购买", interactive=False)
                            shop_s2 = gr.Number(value=0, label="合格", interactive=False)
                            shop_s3 = gr.Number(value=0, label="不合格", interactive=False)
                            shop_s4 = gr.Number(value=0, label="售出", interactive=False)
                        gr.Markdown("### 日志")
                        shop_log = gr.TextArea(label="", lines=12, interactive=False)

            # ── 仓库整理 ──
            with gr.Tab("仓库整理"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 匹配设置")
                        repo_match = gr.Dropdown(["双有效", "三有效"], value="双有效", label="匹配模式")
                        gr.Markdown("### 数量设置")
                        repo_no_limit = gr.Checkbox(value=True, label="不限制")
                        repo_max = gr.Number(value=100, label="最大检测数", interactive=False)
                        with gr.Row():
                            repo_start = gr.Button("开始清理", variant="primary")
                            repo_stop = gr.Button("停止", interactive=False)

                        repo_no_limit.change(
                            lambda x: gr.update(interactive=not x),
                            inputs=repo_no_limit, outputs=repo_max)

                    with gr.Column(scale=2):
                        gr.Markdown("### 统计")
                        with gr.Row():
                            repo_s1 = gr.Number(value=0, label="检测", interactive=False)
                            repo_s2 = gr.Number(value=0, label="合格", interactive=False)
                            repo_s3 = gr.Number(value=0, label="不合格", interactive=False)
                            repo_s4 = gr.Number(value=0, label="售出", interactive=False)
                        gr.Markdown("### 日志")
                        repo_log = gr.TextArea(label="", lines=12, interactive=False)

            # ── 构筑管理 ──
            with gr.Tab("构筑管理"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 构筑列表")
                        build_selector = gr.Dropdown(
                            choices=get_build_names(),
                            label="选择构筑", interactive=True)
                        with gr.Row():
                            new_build_name = gr.Textbox(label="新构筑名称", scale=3)
                            add_build_btn = gr.Button("+", scale=1, min_width=40)
                        del_build_btn = gr.Button("删除选中", variant="stop")
                        build_status = gr.Textbox(label="状态", interactive=False, lines=1)

                        gr.Markdown("### 词条搜索")
                        search_type = gr.Dropdown(
                            ["普通", "深夜正面", "深夜负面", "全部(黑名单)"],
                            value="普通", label="词条库")
                        search_query = gr.Textbox(label="搜索", placeholder="输入关键字...")
                        search_result = gr.TextArea(label="搜索结果", lines=8, interactive=False)

                        search_query.change(search_vocab,
                            inputs=[search_query, search_type], outputs=search_result)
                        search_type.change(search_vocab,
                            inputs=[search_query, search_type], outputs=search_result)

                    with gr.Column(scale=2):
                        gr.Markdown("### 词条配置")
                        gr.Markdown("*每行一条词条，从左侧搜索结果复制粘贴*")
                        with gr.Tabs():
                            with gr.Tab("普通白名单"):
                                build_normal = gr.TextArea(label="", lines=8, placeholder="每行一条词条")
                            with gr.Tab("深夜正面"):
                                build_deepnight = gr.TextArea(label="", lines=8)
                            with gr.Tab("深夜负面"):
                                build_neg = gr.TextArea(label="", lines=8)
                            with gr.Tab("黑名单"):
                                build_blacklist = gr.TextArea(label="", lines=8)
                        save_build_btn = gr.Button("保存", variant="primary")

                        gr.Markdown("### 导入/导出")
                        with gr.Tabs():
                            with gr.Tab("导出"):
                                export_btn = gr.Button("导出全部构筑")
                                export_output = gr.TextArea(label="JSON (复制保存)", lines=6)
                            with gr.Tab("导入"):
                                import_input = gr.TextArea(label="粘贴 JSON", lines=6)
                                import_btn = gr.Button("导入")

                # 事件绑定
                build_selector.change(get_build_data,
                    inputs=build_selector,
                    outputs=[build_normal, build_deepnight, build_neg, build_blacklist])

                add_build_btn.click(add_build,
                    inputs=new_build_name,
                    outputs=[build_selector, build_status])

                del_build_btn.click(delete_build,
                    inputs=build_selector,
                    outputs=[build_selector, build_status])

                save_build_btn.click(save_build,
                    inputs=[build_selector, build_normal, build_deepnight, build_neg, build_blacklist],
                    outputs=[build_selector, build_status])

                export_btn.click(export_builds, outputs=export_output)
                import_btn.click(import_builds,
                    inputs=import_input, outputs=[build_selector, build_status])

            # ── 设置 ──
            with gr.Tab("设置"):
                gr.Markdown("### 出货通知")
                dingtalk_enabled = gr.Checkbox(label="启用钉钉通知", value=False)
                dingtalk_webhook = gr.Textbox(label="Webhook", placeholder="钉钉机器人 Webhook 地址")

                gr.Markdown("### 存档管理")
                steam_path = gr.Textbox(label="Steam 路径", placeholder="留空自动检测")
                backup_dir = gr.Textbox(label="备份目录", value="data/save_backups")

    return app


def main():
    # 强制使用本地前端资源，不从 CDN 加载
    os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"

    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data")
    data_dir = os.path.normpath(data_dir)

    app = create_app(data_dir)
    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        inbrowser=True,
        show_api=False,
        share=False,
    )


if __name__ == "__main__":
    main()
