import utils as utils

receiver_email = "whitepinedvt@gmail.com"  # Enter receiver address
message = """\
Subject: Message from INSIDE the container!

If you're reading this, the container emailed you."""


#shut down instance and email response to white pine dvt
# git merge test 
# merge test 2

utils.send_email(receiver_email, message)
