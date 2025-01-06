from client_side.UI.encryption import RSACipher

# RSA anahtar çifti oluştur
private_key_pem, public_key_pem = RSACipher.generate_keys()

# Anahtarları "keys" klasörüne kaydet
with open("keys/private_key.pem", "wb") as private_file:
    private_file.write(private_key_pem)

with open("keys/public_key.pem", "wb") as public_file:
    public_file.write(public_key_pem)

print("RSA anahtar çifti başarıyla oluşturuldu ve keys klasörüne kaydedildi!")