from unittest import TestCase

from some_agent_like_you.load_memory import context_aware_conversation_generator


class Test(TestCase):
  def test_context_aware_conversation_generator(self):
    turns = (
      dict(
        session_id="e6827af0-c7b1-4544-a680-a645c67bf629",
        user_message="user message 1",
        assistant_response="assistant message 1"
      ),
      dict(
        session_id="5b792c28-0d4b-44db-b233-7da60d4a65d0",
        user_message="user message 2",
        assistant_response="assistant message 2"
      ),
      dict(
        session_id="e6827af0-c7b1-4544-a680-a645c67bf629",
        user_message="user message 1.1",
        assistant_response="assistant message 1.1"
      )
    )

    generator = context_aware_conversation_generator(turns)

    self.assertEqual(
      ("5b792c28-0d4b-44db-b233-7da60d4a65d0", [
        {"role": "user", "content": "user message 2"},
        {"role": "assistant", "content": "assistant message 2"}
      ]),
      next(generator))
    self.assertEqual(
      ("e6827af0-c7b1-4544-a680-a645c67bf629",
       [{"role": "user", "content": "user message 1"},
        {"role": "assistant", "content": "assistant message 1"},
        {"role": "user", "content": "user message 1.1"},
        {"role": "assistant", "content": "assistant message 1.1"}]),
      next(generator))
