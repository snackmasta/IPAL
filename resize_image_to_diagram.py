from PIL import Image

def resize_to_match(src_path, ref_path, out_path):
    # Buka gambar referensi untuk mendapatkan resolusi
    ref_img = Image.open(ref_path)
    ref_size = ref_img.size  # (width, height)
    
    # Buka gambar sumber dan ubah ukurannya
    src_img = Image.open(src_path)
    resized_img = src_img.resize(ref_size, Image.LANCZOS)
    
    # Simpan gambar hasil resize
    resized_img.save(out_path)
    print(f"Gambar {src_path} telah diubah ukurannya menjadi {ref_size} dan disimpan sebagai {out_path}")

if __name__ == "__main__":
    resize_to_match(
        src_path="image.png",
        ref_path="diagram_ipal.png",
        out_path="image_resized.png"
    )
