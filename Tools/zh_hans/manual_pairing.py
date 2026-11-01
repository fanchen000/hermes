#!/usr/bin/env python3
"""Curated Chinese strings for iPhone gateway pairing, security and onboarding."""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
PATH = ROOT / "App/Resources/Localizable.xcstrings"
TRANSLATIONS = {
    "%@ only works on this machine. Give the gateway an address your iPhone can reach, such as its Tailscale name or network address, then pair.": "%@ 只能在这台设备上使用。请为网关设置 iPhone 可以访问的地址，例如 Tailscale 设备名或局域网地址，然后重新配对。",
    "Allow Hermes to use the camera in Settings, or scan the code with the Camera app.": "请在“设置”中允许 Hermes 使用相机，或直接使用系统“相机”扫描二维码。",
    "Anyone who scans this code can use your Hermes. Show it only to devices you own.": "任何扫描此二维码的人都可能使用你的 Hermes。请只向自己拥有的设备展示。",
    "Bot Mode included": "包含智能体模式",
    "Bot Mode included · asks for the password": "包含智能体模式 · 需要密码",
    "Bot Mode password": "智能体模式密码",
    "Bot Mode stays on this device: its backend (%@) is a local address.": "智能体模式仅在本设备可用，因为后端地址（%@）是本地地址。",
    "Bot Mode: %@": "智能体模式：%@",
    "Bot Mode: your Bots, their chats and routines": "智能体模式：你的智能体、对话与例行任务",
    "Camera access is off": "相机权限未开启",
    "Chats, tasks and skills from this gateway": "来自此网关的对话、任务和技能",
    "Checking the gateway…": "正在检查网关…",
    "Connect": "连接",
    "Connect to %@?": "连接到 %@？",
    "Connected to %@": "已连接到 %@",
    "Connecting to %@…": "正在连接 %@…",
    "Edit Gateway…": "编辑网关…",
    "Got it": "知道了",
    "Make sure this device can reach %@: the same network, or Tailscale on.": "请确保本设备能连接到 %@：两台设备需位于同一网络，或已开启 Tailscale。",
    "On your Mac, open the gateway menu and choose Pair a Device.": "在 Mac 上打开网关菜单，选择“配对设备”。",
    "Open the Camera app and point it at the code instead; Hermes opens from there.": "也可以打开系统“相机”扫描二维码，随后会自动打开 Hermes。",
    "Other devices can't reach this address": "其他设备无法访问此地址",
    "Pair a Device": "配对设备",
    "Pairing code found": "已识别配对码",
    "Password for %@": "%@ 的密码",
    "Scan Pairing Code": "扫描配对码",
    "Scan this code with the Camera app on your iPhone or iPad, or with Scan Pairing Code in Hermes.": "请用 iPhone 或 iPad 的系统“相机”扫描此二维码，也可以在 Hermes 中使用“扫描配对码”。",
    "Show Code": "显示二维码",
    "Signing in to Bot Mode…": "正在登录智能体模式…",
    "That isn't a Hermes pairing code.": "这不是有效的 Hermes 配对码。",
    "The API key is saved in this device's Keychain": "API 密钥已保存在此设备的钥匙串中",
    "The code holds your API key. Show it when you're ready to scan.": "二维码包含你的 API 密钥，请在准备扫描时再展示。",
    "This address isn't encrypted and isn't on your network: the API key and your chats would travel readable. Connect only if you trust every network in between.": "此地址未加密且不属于你的本地网络。API 密钥和聊天内容可能以明文传输。只有在确认途经网络均可信时才连接。",
    "This code needs a newer Hermes.": "此配对码需要更新版本的 Hermes。",
    "This code needs a newer Hermes. Update the app, then scan again.": "此配对码需要更新版本的 Hermes。请先更新应用，然后重新扫描。",
    "This device can't scan codes": "此设备无法扫描二维码",
    "Update": "更新",
    "Update %@?": "更新 %@？",
    "You already have a gateway called %@ at another address. Connect only if you made this code yourself.": "你已配置一个同名网关 %@，但地址不同。请确认此二维码由你本人创建后再连接。"
}

def main() -> None:
    catalog = json.loads(PATH.read_text(encoding="utf-8"))
    for key, value in TRANSLATIONS.items():
        existing = catalog["strings"].get(key)
        unit = (existing or {}).get("localizations", {}).get("zh-Hans", {}).get("stringUnit", {})
        if unit.get("state") == "translated":
            continue
        catalog["strings"][key] = {
            "extractionState":"manual",
            "localizations":{"zh-Hans":{"stringUnit":{"state":"translated", "value":value}}},
        }
    catalog["strings"] = dict(sorted(catalog["strings"].items()))
    PATH.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("pairing_strings_reviewed",len(TRANSLATIONS))

if __name__=="__main__":
    main()
