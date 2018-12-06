import re
k = 'SP_MMEScaleIn_{{MME-NODE}}_IN'
match = re.match(r'SP_(.*)_{{(.*?)}}_(.*)', k)
print match.group(1)
print match.group(2)
