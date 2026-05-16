import os
import glob
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def main():
    # --- NASTAVITVE (Spremenljivke za urejanje) ---
    Y_OFFSET = 80          # Odmik SPODNJEGA roba okvirja od spodnjega roba slike
    
    FONT_SIZE = 50         # Velikost pisave
    FONT_PATH = "AzeretMono-Regular.ttf"          # Navadna pisava
    FONT_ITALIC_PATH = "AzeretMono-Italic.ttf"  # Italic pisava za tekst v []
    
    BOX_OPACITY = 120      # Prosojnost pravokotnika (0 = nevidno, 255 = polno)
    BOX_RADIUS = 15        # Zaobljenost vseh zunanjih vogalov
    
    PADDING_X = 20         # Notranji odmik v pravokotniku (levo/desno)
    PADDING_Y = 15         # Notranji odmik v pravokotniku (zgoraj/spodaj)
    # ---------------------------------------------

    # 1. Iskanje datoteke z imenom "tole" ne glede na format
    iskani_vzorec = os.path.join(os.path.dirname(__file__), "tole.*")
    najdene_slike = glob.glob(iskani_vzorec)

    if not najdene_slike:
        print("Napaka: V mapi ni nobene slike z imenom 'tole' (npr. tole.jpg, tole.png ...)")
        return

    pot_do_slike = najdene_slike[0]
    _, koncnica = os.path.splitext(pot_do_slike)

    # 2. Vnos besedila za dve vrstici
    print("Vnesi besedilo (če želiš samo eno vrstico, pusti drugo prazno):")
    vnos1 = input("1. vrstica (zgornja): ").strip()
    vnos2 = input("2. vrstica (spodnja): ").strip()

    # Filtriramo samo tiste vrstice, ki niso prazne
    vrstice = [v for v in [vnos1, vnos2] if v]

    if not vrstice:
        print("Nisi vnesel nobenega besedila. Prekinjam.")
        return

    try:
        # 3. Odpiranje slike
        with Image.open(pot_do_slike) as img:
            img = img.convert("RGBA")
            sirina_slike, visina_slike = img.size
            
            # Glavna prosojna plast za končni izris
            overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
            draw_overlay = ImageDraw.Draw(overlay)

            # 4. Nalaganje fontov
            try:
                font_reg = ImageFont.truetype(FONT_PATH, FONT_SIZE)
            except IOError:
                font_reg = ImageFont.load_default()

            try:
                font_ital = ImageFont.truetype(FONT_ITALIC_PATH, FONT_SIZE)
            except IOError:
                font_ital = font_reg

            def razčleni_tekst(tekst):
                # Če je celoten tekst v oglatih oklepajih, vzamemo vsebino in uporabimo italic font
                if tekst.startswith("[") and tekst.endswith("]"):
                    cisti_tekst = tekst[1:-1]
                    return f"[{cisti_tekst}]", font_ital
                
                # Za navaden tekst ohranimo nespremenjeno obliko
                return tekst, font_reg

            # 5. Izračun dimenzij za vsako vrstico
            podatki_vrstic = []
            for tekst in vrstice:
                končni_tekst, uporabi_font = razčleni_tekst(tekst)
                bbox = draw_overlay.textbbox((0, 0), končni_tekst, font=uporabi_font)
                w = bbox[2] - bbox[0]
                h = bbox[3] - bbox[1]
                offset_y = bbox[1]
                
                podatki_vrstic.append({
                    'tekst': končni_tekst,
                    'font': uporabi_font,
                    'w_tekst': w,
                    'h_tekst': h,
                    'offset_y': offset_y,
                    'w_box': w + (2 * PADDING_X),
                    'h_box': h + (2 * PADDING_Y)
                })

            # 6. Izračun natančnih koordinat (vrstice se stikata)
            trenutni_y_spodaj = visina_slike - Y_OFFSET
            
            for podatek in reversed(podatki_vrstic):
                rect_y2 = trenutni_y_spodaj
                rect_y1 = rect_y2 - podatek['h_box']
                
                rect_x1 = (sirina_slike - podatek['w_box']) // 2
                rect_x2 = rect_x1 + podatek['w_box']
                
                podatek['coords_box'] = [rect_x1, rect_y1, rect_x2, rect_y2]
                trenutni_y_spodaj = rect_y1 

            # 7. Triki z masko za doseganje enakomerno zaobljenih vogalov na stiku
            scale = 4  
            maska = Image.new("L", (sirina_slike * scale, visina_slike * scale), 0)
            draw_mask = ImageDraw.Draw(maska)

            for podatek in podatki_vrstic:
                x1, y1, x2, y2 = podatek['coords_box']
                draw_mask.rectangle([x1 * scale, y1 * scale, x2 * scale, y2 * scale], fill=255)

            if BOX_RADIUS > 0:
                blur_radius = BOX_RADIUS * scale
                maska = maska.filter(ImageFilter.GaussianBlur(blur_radius / 2))
                maska = maska.point(lambda x: 255 if x > 127 else 0)

            maska = maska.resize((sirina_slike, visina_slike), resample=Image.Resampling.LANCZOS)

            # 8. Izrez okvirja z nastavljeno prosojnostjo
            barva_okvirja = Image.new("RGBA", img.size, (0, 0, 0, BOX_OPACITY))
            overlay.paste(barva_okvirja, (0, 0), mask=maska)

            # 9. Izris belega teksta čez pripravljen enoten okvir
            for podatek in podatki_vrstic:
                x1, y1, _, _ = podatek['coords_box']
                tx = x1 + PADDING_X
                ty = y1 + PADDING_Y - podatek['offset_y']
                draw_overlay.text((tx, ty), podatek['tekst'], fill="white", font=podatek['font'])

            # 10. Združevanje in shranjevanje
            končna_slika = Image.alpha_composite(img, overlay).convert("RGB")
            izhodno_ime = f"tole_edited{koncnica}"
            izhodna_pot = os.path.join(os.path.dirname(__file__), izhodno_ime)
            končna_slika.save(izhodna_pot)
            
            print(f"Uspešno shranjeno kot: {izhodno_ime}")

    except Exception as e:
        print(f"Prišlo je do napake pri obdelavi slike: {e}")

if __name__ == "__main__":
    main()