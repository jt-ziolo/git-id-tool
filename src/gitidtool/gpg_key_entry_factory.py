from gitidtool.gpg_key_entry import GpgKeyEntry


class GpgKeyEntryFactory:
    public_key: str
    name: str
    email: str

    def create(self):
        return GpgKeyEntry(self.public_key, self.name, self.email)
