import json
import os
from collections import defaultdict


class Leaf(defaultdict):
    _prefix = None

    def __init__(self, context=None, prefix=None, ofclass=list):
        super(Leaf, self).__init__(ofclass)
        if context:
            self.context = context
        self._prefix = prefix

    def __getattr__(self, key):
        return super(Leaf, self).__getitem__(self._get_key(key))

    def __setattr__(self, key, value):
        try:
            object.__getattr__(self, key)
            object.__setattr__(self, key, value)
        except AttributeError:
            key = self._get_key(key)
            value = self.get_context(value) if key == "@context" else value
            if key[0] == "_":
                object.__setattr__(self, key, value)
            else:
                super(Leaf, self).__setitem__(key, value)

    def __delattr__(self, key):
        return super(Leaf, self).__delitem__(self._get_key(key))

    def _get_key(self, key):
        if key is "context":
            return "@context"
        elif self._prefix:
            return "{}:{}".format(self._prefix, key)
        else:
            return key

    @staticmethod
    def get_context(context):
        if isinstance(context, list):
            contexts = []
            for c in context:
                contexts.append(Response.get_context(c))
            return contexts
        elif isinstance(context, dict):
            return context
        elif isinstance(context, basestring):
            try:
                with open(context) as f:
                    return json.loads(f.read())
            except IOError:
                return context


class Response(Leaf):
    def __init__(self, context=None, *args, **kwargs):
        if context is None:
            context = "{}/context.jsonld".format(os.path.dirname(
                os.path.realpath(__file__)))
        super(Response, self).__init__(*args, context=context, **kwargs)
        self["analysis"] = []
        self["entries"] = []


class Entry(Leaf):
    def __init__(self, text=None, emotion_sets=None, opinions=None, **kwargs):
        super(Entry, self).__init__(**kwargs)
        if text:
            self.text = text
        if emotion_sets:
            self.emotionSets = emotion_sets
        if opinions:
            self.opinions = opinions


class Opinion(Leaf):
    opinionContext = {}
    def __init__(self, polarityValue=None, hasPolarity=None, *args, **kwargs):
        super(Opinion, self).__init__(context=self.opinionContext,
                                      *args,
                                      **kwargs)
        if polarityValue is not None:
            self.polarityValue = polarityValue
        if hasPolarity is not None:
            self.hasPolarity = hasPolarity


class EmotionSet(Leaf):
    emotionContext = {}
    def __init__(self, emotions=None, *args, **kwargs):
        if not emotions:
            emotions = []
        super(EmotionSet, self).__init__(context=self.emotionContext,
                                         *args,
                                         **kwargs)
        self.emotions = emotions or []
