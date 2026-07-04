import Foundation
import AVFoundation
import Speech

/// 基于苹果 Speech 框架的实时语音转文字，iOS 与 macOS 通用。
/// 边说边出字（partial results），支持普通话 / 国语（台湾）/ 英语等。
final class SpeechRecognizer: NSObject, ObservableObject {
    @Published var transcript = ""
    @Published var isRecording = false
    @Published var errorMessage: String?

    private let audioEngine = AVAudioEngine()
    private var request: SFSpeechAudioBufferRecognitionRequest?
    private var task: SFSpeechRecognitionTask?

    // MARK: - 权限

    static func requestPermissions(_ completion: @escaping (Bool) -> Void) {
        SFSpeechRecognizer.requestAuthorization { auth in
            guard auth == .authorized else {
                completion(false)
                return
            }
            #if os(iOS)
            AVAudioSession.sharedInstance().requestRecordPermission { granted in
                completion(granted)
            }
            #else
            AVCaptureDevice.requestAccess(for: .audio) { granted in
                completion(granted)
            }
            #endif
        }
    }

    // MARK: - 开始 / 停止

    func start(localeIdentifier: String) {
        guard !isRecording else { return }
        errorMessage = nil
        SpeechRecognizer.requestPermissions { [weak self] granted in
            DispatchQueue.main.async {
                guard let self else { return }
                guard granted else {
                    self.errorMessage = "请在系统设置里允许「麦克风」和「语音识别」权限"
                    return
                }
                do {
                    try self.beginSession(localeIdentifier: localeIdentifier)
                } catch {
                    self.errorMessage = "无法启动录音：\(error.localizedDescription)"
                    self.teardown()
                }
            }
        }
    }

    func stop() {
        guard isRecording else { return }
        request?.endAudio()
        teardown()
    }

    // MARK: - 内部实现

    private func beginSession(localeIdentifier: String) throws {
        guard let recognizer = SFSpeechRecognizer(locale: Locale(identifier: localeIdentifier)),
              recognizer.isAvailable else {
            errorMessage = "当前语言的语音识别暂不可用（部分语言首次使用需要联网）"
            return
        }

        #if os(iOS)
        let session = AVAudioSession.sharedInstance()
        try session.setCategory(.record, mode: .measurement, options: .duckOthers)
        try session.setActive(true, options: .notifyOthersOnDeactivation)
        #endif

        let request = SFSpeechAudioBufferRecognitionRequest()
        request.shouldReportPartialResults = true
        self.request = request

        let inputNode = audioEngine.inputNode
        let format = inputNode.outputFormat(forBus: 0)
        inputNode.installTap(onBus: 0, bufferSize: 1024, format: format) { buffer, _ in
            request.append(buffer)
        }
        audioEngine.prepare()
        try audioEngine.start()

        transcript = ""
        isRecording = true

        task = recognizer.recognitionTask(with: request) { [weak self] result, error in
            DispatchQueue.main.async {
                guard let self else { return }
                if let result {
                    self.transcript = result.bestTranscription.formattedString
                }
                if let error, self.isRecording {
                    // 用户主动 stop 后收到的收尾回调不算错误
                    self.errorMessage = "识别中断：\(error.localizedDescription)"
                    self.teardown()
                } else if result?.isFinal == true {
                    self.teardown()
                }
            }
        }
    }

    private func teardown() {
        if audioEngine.isRunning {
            audioEngine.stop()
        }
        audioEngine.inputNode.removeTap(onBus: 0)
        task?.finish()
        task = nil
        request = nil
        isRecording = false
        #if os(iOS)
        try? AVAudioSession.sharedInstance().setActive(false, options: .notifyOthersOnDeactivation)
        #endif
    }
}
