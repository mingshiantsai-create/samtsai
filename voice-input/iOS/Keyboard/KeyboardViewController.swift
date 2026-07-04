import UIKit

/// 自定义键盘：显示主 App 识别出的语音文字，一键插入到当前输入框。
/// 说明：苹果不允许键盘扩展直接使用麦克风，所以录音在主 App 完成，
/// 这里通过 App Group 共享数据读取结果。
final class KeyboardViewController: UIInputViewController {

    private let latestButton = UIButton(type: .system)
    private let historyStack = UIStackView()
    private var heightConstraint: NSLayoutConstraint?
    private var deleteTimer: Timer?

    // MARK: - 生命周期

    override func viewDidLoad() {
        super.viewDidLoad()
        buildUI()
    }

    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        reloadHistory()
    }

    override func updateViewConstraints() {
        super.updateViewConstraints()
        if heightConstraint == nil {
            let c = view.heightAnchor.constraint(equalToConstant: 260)
            c.priority = UILayoutPriority(999)
            c.isActive = true
            heightConstraint = c
        }
    }

    // MARK: - UI

    private func buildUI() {
        let root = UIStackView()
        root.axis = .vertical
        root.spacing = 6
        root.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(root)
        NSLayoutConstraint.activate([
            root.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 6),
            root.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -6),
            root.topAnchor.constraint(equalTo: view.topAnchor, constant: 8),
            root.bottomAnchor.constraint(equalTo: view.bottomAnchor, constant: -8),
        ])

        // 第一行：去录音 + 插入最新
        let topRow = UIStackView()
        topRow.axis = .horizontal
        topRow.spacing = 6
        topRow.distribution = .fillProportionally

        let micButton = makeKey(title: "🎤 去录音", background: .systemBlue, textColor: .white)
        micButton.addTarget(self, action: #selector(openContainerApp), for: .touchUpInside)

        latestButton.setTitle("（暂无内容）", for: .normal)
        styleKey(latestButton, background: .systemGreen, textColor: .white)
        latestButton.titleLabel?.lineBreakMode = .byTruncatingTail
        latestButton.addTarget(self, action: #selector(insertLatest), for: .touchUpInside)

        topRow.addArrangedSubview(micButton)
        topRow.addArrangedSubview(latestButton)
        micButton.widthAnchor.constraint(equalTo: topRow.widthAnchor, multiplier: 0.32).isActive = true
        root.addArrangedSubview(topRow)

        // 历史记录区（最多 3 条）
        historyStack.axis = .vertical
        historyStack.spacing = 6
        historyStack.distribution = .fillEqually
        root.addArrangedSubview(historyStack)

        // 底部功能行：地球 / 空格 / 删除 / 换行
        let bottomRow = UIStackView()
        bottomRow.axis = .horizontal
        bottomRow.spacing = 6
        bottomRow.distribution = .fillProportionally

        if needsInputModeSwitchKey {
            let globe = makeKey(title: "🌐", background: .tertiarySystemFill, textColor: .label)
            globe.addTarget(self,
                            action: #selector(handleInputModeList(from:with:)),
                            for: .allTouchEvents)
            bottomRow.addArrangedSubview(globe)
        }

        let space = makeKey(title: "空格", background: .tertiarySystemFill, textColor: .label)
        space.addTarget(self, action: #selector(insertSpace), for: .touchUpInside)

        let delete = makeKey(title: "⌫", background: .tertiarySystemFill, textColor: .label)
        delete.addTarget(self, action: #selector(deleteBackwardTapped), for: .touchUpInside)
        let longPress = UILongPressGestureRecognizer(target: self, action: #selector(deleteLongPress(_:)))
        delete.addGestureRecognizer(longPress)

        let ret = makeKey(title: "换行", background: .tertiarySystemFill, textColor: .label)
        ret.addTarget(self, action: #selector(insertReturn), for: .touchUpInside)

        bottomRow.addArrangedSubview(space)
        bottomRow.addArrangedSubview(delete)
        bottomRow.addArrangedSubview(ret)
        space.widthAnchor.constraint(equalTo: bottomRow.widthAnchor, multiplier: 0.4).isActive = true
        root.addArrangedSubview(bottomRow)
        bottomRow.heightAnchor.constraint(equalToConstant: 44).isActive = true
        topRow.heightAnchor.constraint(equalToConstant: 48).isActive = true
    }

    private func makeKey(title: String, background: UIColor, textColor: UIColor) -> UIButton {
        let button = UIButton(type: .system)
        button.setTitle(title, for: .normal)
        styleKey(button, background: background, textColor: textColor)
        return button
    }

    private func styleKey(_ button: UIButton, background: UIColor, textColor: UIColor) {
        button.backgroundColor = background
        button.setTitleColor(textColor, for: .normal)
        button.titleLabel?.font = .systemFont(ofSize: 17, weight: .medium)
        button.layer.cornerRadius = 8
        button.contentEdgeInsets = UIEdgeInsets(top: 6, left: 10, bottom: 6, right: 10)
    }

    private func reloadHistory() {
        let history = SharedStore.history

        if let latest = history.first {
            latestButton.setTitle("插入：\(snippet(latest))", for: .normal)
            latestButton.isEnabled = true
        } else {
            latestButton.setTitle("（先去主 App 录音）", for: .normal)
            latestButton.isEnabled = false
        }

        historyStack.arrangedSubviews.forEach { $0.removeFromSuperview() }
        for (index, item) in history.dropFirst().prefix(3).enumerated() {
            let button = makeKey(title: snippet(item),
                                 background: .secondarySystemFill,
                                 textColor: .label)
            button.contentHorizontalAlignment = .left
            button.titleLabel?.lineBreakMode = .byTruncatingTail
            button.tag = index + 1
            button.addTarget(self, action: #selector(insertHistory(_:)), for: .touchUpInside)
            historyStack.addArrangedSubview(button)
        }
    }

    private func snippet(_ text: String) -> String {
        text.count > 22 ? String(text.prefix(22)) + "…" : text
    }

    // MARK: - 按键动作

    @objc private func insertLatest() {
        if let latest = SharedStore.latest {
            textDocumentProxy.insertText(latest)
        }
    }

    @objc private func insertHistory(_ sender: UIButton) {
        let history = SharedStore.history
        if history.indices.contains(sender.tag) {
            textDocumentProxy.insertText(history[sender.tag])
        }
    }

    @objc private func insertSpace() {
        textDocumentProxy.insertText(" ")
    }

    @objc private func insertReturn() {
        textDocumentProxy.insertText("\n")
    }

    @objc private func deleteBackwardTapped() {
        textDocumentProxy.deleteBackward()
    }

    @objc private func deleteLongPress(_ gesture: UILongPressGestureRecognizer) {
        switch gesture.state {
        case .began:
            deleteTimer = Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { [weak self] _ in
                self?.textDocumentProxy.deleteBackward()
            }
        case .ended, .cancelled, .failed:
            deleteTimer?.invalidate()
            deleteTimer = nil
        default:
            break
        }
    }

    /// 键盘扩展不能直接拿到 UIApplication，用 responder chain 方式跳回主 App 录音。
    @objc private func openContainerApp() {
        guard let url = URL(string: "voiceinput://record") else { return }
        let selector = sel_registerName("openURL:")
        var responder: UIResponder? = self
        while let current = responder {
            if current.responds(to: selector) {
                current.perform(selector, with: url)
                return
            }
            responder = current.next
        }
    }
}
