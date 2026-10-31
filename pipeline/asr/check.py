import sherpa_onnx, numpy as np, os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sherpa-onnx-zipformer-korean-2024-06-24') + '/'
_rec = None
def rec():
    global _rec
    if _rec is None:
        _rec = sherpa_onnx.OfflineRecognizer.from_transducer(encoder=D+'encoder-epoch-99-avg-1.int8.onnx', decoder=D+'decoder-epoch-99-avg-1.int8.onnx',
                    joiner=D+'joiner-epoch-99-avg-1.int8.onnx', tokens=D+'tokens.txt', num_threads=2, decoding_method='greedy_search')
    return _rec
def hear(samples, sr):
    x = np.asarray(samples, dtype=np.float32)
    pad = np.zeros(int(sr * 0.3), dtype=np.float32)
    x = np.concatenate([pad, x, pad])
    s = rec().create_stream(); s.accept_waveform(sr, x); rec().decode_stream(s)
    return s.result.text.strip()
