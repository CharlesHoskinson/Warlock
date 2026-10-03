"""QA output-only adapter: never opens a synthesizer, audio or braille device."""
import json
import os
import time
from orca.speechserver import SpeechServer as Base, VoiceFamily, SayAllContext


def write(kind, text='', **extra):
    with open(os.environ['ORCA_QA_UTTERANCES'], 'a', encoding='utf-8') as stream:
        stream.write(json.dumps(dict(time=time.monotonic(), kind=kind, text=text, **extra), ensure_ascii=False) + '\n')


class SpeechServer(Base):
    @staticmethod
    def get_factory_name():
        return 'Silent QA speech log'

    @staticmethod
    def get_speech_server(info=None):
        return SpeechServer()

    @staticmethod
    def get_speech_servers():
        return [SpeechServer()]

    def get_info(self):
        return ['Silent QA speech log', 'silent-qa']

    def get_voice_families(self):
        return [VoiceFamily({'name': 'QA', 'lang': 'en', 'dialect': 'US'})]

    def speak(self, text=None, acss=None):
        write('speech', text or '', voice=dict(acss or {}))

    def speak_character(self, character, acss=None, cap_style=None):
        write('character', character)

    def speak_key_event(self, event, acss=None):
        write('key', event.get_key_name())

    def say_all(self, iterator, callback):
        for context, acss in iterator:
            write('say-all', context.utterance)
            callback(context, SayAllContext.COMPLETED)

    def stop(self):
        write('stop')

    def is_alive(self):
        return True
