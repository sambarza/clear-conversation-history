import time
from cat.mad_hatter.decorators import tool, hook
from cat.looking_glass.cheshire_cat import CheshireCat

original_user_message_json = ""

@hook
def agent_fast_reply(fast_reply, cat: CheshireCat):
   """Use this hook to reply fast to the user"""

   if cat.working_memory["user_message_json"]["text"] == ".p":

      return formatted_chat_history(cat)

   if cat.working_memory["user_message_json"]["text"] == ".cc":

      cat.working_memory.episodic_memory.clear()
      cat.working_memory.history.clear()

      return {
            "output": "Ok I have forgotten everything"
      }
   
   if cat.working_memory["user_message_json"]["text"] == ".lp":

      return {
            "output": cat.working_memory.last_used_prompt
      }
   
   if cat.working_memory["user_message_json"]["text"] == ".rl":
      cat.working_memory.remove_last_turn()
      return {
            "output": "Ok I have removed the last turn"
      }

   if cat.working_memory["user_message_json"]["text"][:2] == ".k":
      turns_to_keep = int(cat.working_memory["user_message_json"]["text"].split(" ")[1])

      cat.working_memory.keep_up_to_turn(turns_to_keep)

      return formatted_chat_history(cat)
   
   if "original_text" in cat.working_memory["user_message_json"].keys():
      
      original_user_message_text = cat.working_memory["user_message_json"]["original_text"]

      if original_user_message_text[:2] == ".r":
      
         # Answer to resend has been specified?
         if len(original_user_message_text.split(" ")) > 1:
            # Answer to resend has been specified
            question_to_resend = int(original_user_message_text.split(" ")[1])
         else:
            # Answer to resend has not been specified, resend the last answer
            question_to_resend = int(len(cat.working_memory["history"]) - 1)

         # Keep the history up to the answer to resend
         turns_to_keep = question_to_resend - 1

         # Keep the history up to the answer to resend
         cat.working_memory.keep_up_to_turn(turns_to_keep)

         # The question has been already replaced in before_cat_reads_message hook
         ##cat.working_memory["user_message_json"]["text"] = question

         # Remove the original message
         del cat.working_memory["user_message_json"]["original_text"]

         return None

   if cat.working_memory["user_message_json"]["text"] == ".":

      commands = """
      Commands:
      [.p]     - Print Chat history
      [.k nnn] - Keep Chat History up to nnn turns
      [.r]     - Resend the last question
      [.r nnn] - Resend a specific question
      [.cc]    - Clear Chat history
      [.rl]    - Remove Last turn
      [.lp]    - Last Prompt
      """

      return {
            "output": commands
      }
   

def formatted_chat_history(cat):

   history = ""

   turn_number = 0
   for turn in cat.working_memory.history:
      turn_number += 1

      history += f"\n *{str(turn_number).zfill(3)}* - {turn['who']}: {turn['message']}"

   return {
         "output": history
   }

@hook
def before_cat_reads_message(user_message_json, cat: CheshireCat):

   # Exit if not resend command
   if not user_message_json["text"][:2] == ".r":
      return

   # Keep the original message, will be used in hook agent_fast_reply
   user_message_json["original_text"] = user_message_json["text"]

   # Answer to resend has been specified?
   if len(user_message_json["text"].split(" ")) > 1:
      # Answer to resend has been specified
      question_to_resend = int(user_message_json["text"].split(" ")[1])
   else:
      # Answer to resend has not been specified, resend the last answer
      question_to_resend = int(len(cat.working_memory["history"]) - 1)

   # Get the question
   question = cat.working_memory["history"][question_to_resend - 1]["message"]
   
   user_message_json["text"] = question

   return user_message_json