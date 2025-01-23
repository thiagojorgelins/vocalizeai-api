from pydub import AudioSegment
from pydub.silence import detect_nonsilent


def segment_data(file_path, final_padding=200, min_silence_len=300, silence_thresh=-40):
    """
    Segmenta o áudio em partes não silenciosas e retorna os segmentos processados.
    Args:
        file_path: Caminho do arquivo de áudio.
        final_padding: Padding final adicionado em milissegundos.
        min_silence_len: Duração mínima do silêncio (ms).
        silence_thresh: Limite de volume para considerar silêncio.
    Returns:
        Lista de dicionários com dados dos segmentos.
    """
    audio = AudioSegment.from_file(file_path, format="wav")
    nonsilent_ranges = detect_nonsilent(
        audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh
    )

    segments_info = []

    for idx, (start, end) in enumerate(nonsilent_ranges):
        # Adiciona padding ao início e ao final
        start = max(0, start - final_padding)
        end = min(len(audio), end + final_padding)

        segment = audio[start:end]
        segments_info.append(
            {
                "segment_data": segment,
                "start_time": start / 1000,
                "end_time": end / 1000,
                "duration": (end - start) / 1000,
            }
        )

    return segments_info
