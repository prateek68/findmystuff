####FACEBOOK POST########
# *name* (*email*) has lost/found *itemname* at *location*
# content of the post that's posted on FB.

FB_LOST_ITEM_POST = """%(name)s (%(email)s) has lost %(itemname)s at %(location)s.
Additional Details: %(details)s."""

FB_FOUND_ITEM_POST = """%(name)s (%(email)s) has found %(itemname)s at %(location)s.
Additional Details: %(details)s."""


#### NOTIFICATION EMAIL ####
# subject/body of the mails sent when items are reported lost/found.

EMAIL_FOUND_YOUR_ITEM_SUBJECT = "Great news! We've found your '%(itemname)s'."
EMAIL_FOUND_YOUR_ITEM = """Hi %(self_name)s,

We have found your '%(itemname)s'. It seems that %(name)s has found it. You can contact him/her at %(email)s.
If the '%(itemname)s' found by %(name)s isn't yours, please click findmystuff.iiitd.edu.in%(link)s to reopen it in the portal.

Thanks,
Find My Stuff - IIITD"""


EMAIL_FOUND_OWNER_SUBJECT = "Great news! We've found who '%(itemname)s' belongs to."
EMAIL_FOUND_OWNER = """Hi %(self_name)s,

It seems that '%(itemname)s' that you've found belongs to %(name)s. You can contact him/her at %(email)s.
If it doesn't belong to %(name)s, please click findmystuff.iiitd.edu.in%(link)s to reopen it in the portal.

Thanks,
Find My Stuff - IIITD"""
