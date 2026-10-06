# Actual background-effect protocol fixture

Preserve all original native child/modal/popup/root buffer commands, counts, bounds, server barriers and cleanup. Add exact ext-background-effect-v1 manager capability binding and real root-surface create/pending-region/change/clear/destroy commands. New commands do not commit a buffer; explicit existing root-commit applies the protocol state. Cleanup retires objects before their owning surfaces/manager. Compile actual scanner output and all dependency TUs with Werror; compilation does not qualify native protocol behavior or blur pixels.
