import sys
import os
import json
import numpy as np
import scipy.io
import librosa
import argparse
import whisperx
import whisper
from whisper.tokenizer import get_tokenizer

# Global file descriptor variable, defaulting to None
FD = None


def send_pipe_message(message):
    global FD
    if FD is not None:
        os.write(FD, message.encode("utf-8") + b"\n")
        # os.fsync(FD)


def load_model():
    """
    This function loads the Whisper ASR-model

    :return model: Whisper ASR-model object
    """

    DEVICE = "cpu"
    COMPUTE_TYPE = "int8"

    tokenizer = get_tokenizer(multilingual=True)

    # Ensure numbers are suppressed in the transcript
    number_tokens = [
        i
        for i in range(tokenizer.eot)
        if all(c in "0123456789" for c in tokenizer.decode([i]).strip())
    ]

    model = whisperx.load_model(
        "medium",
        device=DEVICE,
        compute_type=COMPUTE_TYPE,
        language="de",
        asr_options={
            "suppress_tokens": [-1] + number_tokens,
            "hotwords": [],  # Provide an empty list if no hotwords are needed
        },
    )

    send_pipe_message(
        "ready"
    )  # Signal that the model is loaded and ready only if FD is provided
    return model


def process(a_model, bs, inp_path_audio, out_path_json):
    """
    This function generates the transcript of the speech signal provided by inp_path_audio with the Whisper
    speech recognition model provided by a_model and writes the results to the .json-file specified by out_path_json.

    :param a_model: Whisper ASR-Model object
    :param bs: Int
    :param inp_path_audio: String
    :param out_path_json: String
    """

    FS_TARGET = 16000

    # Load the speech signal
    fs, audio_data = scipy.io.wavfile.read(inp_path_audio)

    if audio_data.size == 0:
        return sys.stdout.write("Audio Data empty!")

    # Ensure the speech signal has a suitable sampling rate.
    audio_data = audio_data.astype(np.float32)
    audio_data = audio_data / (np.max(np.abs(audio_data)) + np.finfo(float).eps)

    if fs != FS_TARGET:
        audio_data = librosa.resample(audio_data, orig_sr=fs, target_sr=FS_TARGET)

    # Generate the transcript
    res = a_model.transcribe(audio_data, batch_size=bs)

    # Postprocess the transcript
    text = ""
    for r in res["segments"]:
        text += r["text"]
        text += " "

    text = text.strip()
    out_dict = {"Text": text}

    # Save the transcript to a .json-file
    with open(out_path_json, "w") as f:
        json.dump(out_dict, f, ensure_ascii=False)

    send_pipe_message("done")


def read_io_paths():
    return sys.stdin.readline().strip().split(",")


def main():
    parser = argparse.ArgumentParser(description="Process audio files with Whisper.")
    parser.add_argument(
        "-f", "--fd", type=int, help="Optional file descriptor for pipe communication"
    )
    args = parser.parse_args()

    if args.fd:
        global FD
        FD = args.fd  # Set the global file descriptor only if provided

    BATCH_SIZE = 16
    asr_model = load_model()
    while True:
        input_path, output_path = read_io_paths()
        if input_path == "exit" and output_path == "exit":
            break
        process(asr_model, BATCH_SIZE, input_path, output_path)


if __name__ == "__main__":
    main()
