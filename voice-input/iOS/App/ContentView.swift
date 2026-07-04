import SwiftUI

struct ContentView: View {
    @StateObject private var speech = SpeechRecognizer()
    @State private var localeID = "zh-TW"
    @State private var history = SharedStore.history
    @State private var showCopiedToast = false

    private let languages: [(id: String, name: String)] = [
        ("zh-TW", "國語（台灣）"),
        ("zh-CN", "普通话"),
        ("en-US", "English"),
        ("yue-CN", "粤语"),
        ("ja-JP", "日本語"),
    ]

    var body: some View {
        NavigationStack {
            VStack(spacing: 16) {
                Picker("识别语言", selection: $localeID) {
                    ForEach(languages, id: \.id) { lang in
                        Text(lang.name).tag(lang.id)
                    }
                }
                .pickerStyle(.segmented)
                .disabled(speech.isRecording)

                transcriptCard

                if let error = speech.errorMessage {
                    Text(error)
                        .font(.footnote)
                        .foregroundStyle(.red)
                        .multilineTextAlignment(.center)
                }

                recordButton

                Text(speech.isRecording
                     ? "正在聆听…再按一下结束"
                     : "说完的内容会自动复制到剪贴板，\n并出现在「语音输入法」键盘里，随处可插入")
                    .font(.footnote)
                    .foregroundStyle(.secondary)
                    .multilineTextAlignment(.center)

                historySection
            }
            .padding()
            .navigationTitle("语音输入")
            .onOpenURL { url in
                // 键盘上的 🎤 按钮通过 voiceinput://record 跳转过来，直接开录
                if url.host == "record" || url.absoluteString.contains("record") {
                    if !speech.isRecording {
                        speech.start(localeIdentifier: localeID)
                    }
                }
            }
            .overlay(alignment: .top) {
                if showCopiedToast {
                    Text("已复制到剪贴板 ✓")
                        .font(.footnote.bold())
                        .padding(.horizontal, 14)
                        .padding(.vertical, 8)
                        .background(.thinMaterial, in: Capsule())
                        .transition(.move(edge: .top).combined(with: .opacity))
                }
            }
        }
    }

    private var transcriptCard: some View {
        ScrollView {
            Text(speech.transcript.isEmpty
                 ? (speech.isRecording ? "请开始说话…" : "按下方按钮开始说话")
                 : speech.transcript)
                .font(.title3)
                .foregroundStyle(speech.transcript.isEmpty ? .secondary : .primary)
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding()
        }
        .frame(maxHeight: 180)
        .background(Color(.secondarySystemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 14))
    }

    private var recordButton: some View {
        Button {
            if speech.isRecording {
                speech.stop()
                saveResult()
            } else {
                speech.start(localeIdentifier: localeID)
            }
        } label: {
            ZStack {
                Circle()
                    .fill(speech.isRecording ? Color.red : Color.accentColor)
                    .frame(width: 96, height: 96)
                Image(systemName: speech.isRecording ? "stop.fill" : "mic.fill")
                    .font(.system(size: 38))
                    .foregroundStyle(.white)
            }
        }
        .buttonStyle(.plain)
        .animation(.easeInOut(duration: 0.2), value: speech.isRecording)
    }

    private var historySection: some View {
        Group {
            if !history.isEmpty {
                List {
                    Section("历史记录（键盘里可直接插入）") {
                        ForEach(Array(history.enumerated()), id: \.offset) { index, item in
                            Button {
                                UIPasteboard.general.string = item
                                flashCopiedToast()
                            } label: {
                                HStack {
                                    Text(item).lineLimit(2)
                                    Spacer()
                                    Image(systemName: "doc.on.doc")
                                        .foregroundStyle(.secondary)
                                }
                            }
                            .tint(.primary)
                            .swipeActions {
                                Button(role: .destructive) {
                                    SharedStore.remove(at: index)
                                    history = SharedStore.history
                                } label: {
                                    Label("删除", systemImage: "trash")
                                }
                            }
                        }
                    }
                }
                .listStyle(.insetGrouped)
                .scrollContentBackground(.hidden)
            } else {
                Spacer()
            }
        }
    }

    private func saveResult() {
        let text = speech.transcript.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty else { return }
        SharedStore.save(text)
        history = SharedStore.history
        UIPasteboard.general.string = text
        flashCopiedToast()
    }

    private func flashCopiedToast() {
        withAnimation { showCopiedToast = true }
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.6) {
            withAnimation { showCopiedToast = false }
        }
    }
}

#Preview {
    ContentView()
}
