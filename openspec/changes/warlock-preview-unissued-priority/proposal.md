# Capture admission after reopening

The dynamic host currently resumes older actors before visiting an unissued
subject. A two-item pool can therefore starve the third subject across repeated
picker openings even when explicit successor enrollment is valid. Visit current
unissued subjects first while preserving all native physical and presentation
guards. This additive change alters no frozen scenario or deadline.
