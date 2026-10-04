def same(before,after):
 if type(before) is not dict or type(after) is not dict:return False
 return all(before.get(k)==after.get(k) for k in ('identity','native','wire','nativeRole','nativePopup','grab','nativeFocus','identity'))
