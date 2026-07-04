# 语音输入法（iPhone / iPad / Mac）

一套基于苹果原生 **Speech 框架** 的语音输入方案，全部离线代码、无第三方服务：

| 平台 | 形态 | 用法 |
|------|------|------|
| iPhone / iPad | 主 App + 自定义键盘扩展 | 主 App 录音转文字 → 任何 App 里切到「语音输入法」键盘一键插入 |
| Mac | 菜单栏应用 | 按全局快捷键 `⌃⌥D` 开始说话，文字**实时打进**当前应用的光标处 |

支持 國語（台灣）/ 普通话 / 粤语 / English / 日本語，边说边出字。

## 为什么 iOS 端要分成「App + 键盘」两部分？

苹果**禁止第三方键盘扩展访问麦克风**（系统限制，无法绕过）。所以：

1. 在主 App 里按 🎤 说话 → 识别结果自动**复制到剪贴板**，并存入共享历史
2. 回到微信 / 备忘录等任何 App，切换到「语音输入法」键盘
3. 键盘顶部会显示最新识别结果，点一下即插入（也可以直接长按粘贴）
4. 键盘上的「🎤 去录音」按钮可直接跳回主 App 继续录音

Mac 没有这个限制，所以 Mac 端是真正的"全局语音打字"。

## 目录结构

```
voice-input/
├── project.yml              # XcodeGen 工程描述（生成 .xcodeproj）
├── Shared/                  # iOS / macOS 共用代码
│   ├── SharedStore.swift    # App Group 共享存储（App ↔ 键盘）
│   └── SpeechRecognizer.swift  # 实时语音转文字
├── iOS/
│   ├── App/                 # iPhone/iPad 主 App（SwiftUI）
│   └── Keyboard/            # 自定义键盘扩展
└── macOS/                   # Mac 菜单栏应用（快捷键 + 模拟打字）
```

## 编译安装（需要一台 Mac + Xcode）

### 0. 前置条件

- macOS 上安装 **Xcode 15 或更新**（App Store 免费下载）
- 一个 Apple ID（免费账号即可真机安装，但 App 每 7 天需重新安装一次；
  付费开发者账号 $99/年 则一年有效）
- 安装 XcodeGen：`brew install xcodegen`

### 1. 生成 Xcode 工程

```bash
cd voice-input
xcodegen generate
open VoiceInput.xcodeproj
```

### 2. 配置签名（三个 target 都要做）

在 Xcode 左侧选中项目 → 依次选中 `VoiceInput-iOS`、`VoiceKeyboard`、`VoiceInput-Mac`
→ **Signing & Capabilities** 标签页：

1. **Team** 选择你的 Apple ID
2. 把 Bundle Identifier 里的 `com.example` 改成你自己的（例如 `com.samtsai`），
   注意键盘扩展必须保持 `主App的BundleID.keyboard` 的形式
3. 如果改了 Bundle ID，**App Group** 也要同步改：
   - 两个 iOS target 的 App Groups 改成如 `group.com.samtsai.voiceinput`
   - 同时修改 `Shared/SharedStore.swift` 顶部的 `appGroupID` 常量
   - 重新 `xcodegen generate` 前建议直接改 `project.yml` 里的对应值

### 3. 安装到 iPhone / iPad

1. 用数据线连接 iPhone/iPad，顶部设备选择器选中你的设备
2. Scheme 选 `VoiceInput-iOS`，按 `⌘R` 运行
3. 首次运行免费账号需在手机上信任开发者：
   设置 → 通用 → VPN与设备管理 → 信任你的 Apple ID
4. **启用键盘**：设置 → 通用 → 键盘 → 键盘 → 添加新键盘 → 选「语音输入法」
5. （可选）点进「语音输入法」打开**允许完全访问**，键盘才能读到共享历史
6. 在任何 App 里长按键盘上的 🌐 切换到语音输入法

iPad 步骤完全相同（同一个 App 通用）。

### 4. 安装到 Mac

1. Scheme 切换为 `VoiceInput-Mac`，`⌘R` 运行（或 Product → Archive 导出 .app）
2. 首次启动按提示授予三个权限：
   - **麦克风**、**语音识别**（弹窗允许即可）
   - **辅助功能**：系统设置 → 隐私与安全性 → 辅助功能 → 勾选「语音输入」
     （没有这个权限就无法模拟打字）
3. 菜单栏会出现 🎤 图标。把光标点到任何输入框，按 **⌃⌥D**（Control+Option+D）
   开始说话，文字会实时打进去；再按一次 ⌃⌥D 停止
4. 想开机自启：系统设置 → 通用 → 登录项 → 添加本应用

## 常见问题

- **识别不出字？** 中文识别首次使用可能需要联网；也可在
  设置 → 通用 → 键盘 → 启用听写 中下载离线语言包后支持离线识别。
- **键盘上的「🎤 去录音」点了没反应？** 个别 iOS 版本限制键盘跳转,
  手动切回主 App 录音即可，结果照常同步到键盘。
- **键盘看不到历史记录？** 确认开启了「允许完全访问」，且 App Group
  三处（两个 entitlements + SharedStore.swift）的 ID 一致。
- **Mac 上按快捷键没输入文字？** 检查「辅助功能」权限；如果改过代码重新编译，
  需要在辅助功能列表里移除后重新添加一次。
- **免费账号 7 天过期**：重新连接 Xcode 运行一次即可续期。

## 技术要点

- 语音识别：`SFSpeechRecognizer` + `AVAudioEngine`，partial results 实时出字
- iOS App ↔ 键盘通信：App Group `UserDefaults`
- Mac 全局快捷键：Carbon `RegisterEventHotKey`（无需额外权限）
- Mac 模拟打字：`CGEvent.keyboardSetUnicodeString`（每次 ≤20 个 UTF-16 字符分块发送），
  「边说边输入」模式通过与已注入文本做差量、退格修正实现实时纠错
