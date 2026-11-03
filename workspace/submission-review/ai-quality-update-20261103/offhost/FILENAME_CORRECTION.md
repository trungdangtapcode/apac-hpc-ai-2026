# Download filename correction

The upload and download completed. The first verifier then looked for the local
source name `VNUHCM - TripleU.zip`, but the returned GitHub asset name was
`VNUHCM.-.TripleU.zip`. This was a filename lookup failure, not a failed hash
comparison. The downloaded bytes were retained. The follow-up verifier matches
all expected files by both original size and SHA-256, records the actual remote
asset names and checks that the downloaded asset manifest is unchanged. No
submission, model result or uploaded data object was replaced.
