# ATK-Pro – Atalar Karo Yeniden Yapıcı
**Not:** Bu proje tamamen tek bir kişi tarafından geliştirilmekte, sürdürülmekte ve desteklenmektedir. Her türlü geri bildirim, rapor veya katkı memnuniyetle karşılanır, ancak geliştirmenin arkasında bir ekip veya kurumsal yapı bulunmamaktadır.
## Açıklama
ATK-Pro, Antenati portalından dijitalleştirilmiş soy ağacı resim ve belgelerinin yeniden yapılandırılması, arşivlenmesi ve danışılması için gelişmiş bir araçtır. Proje, çok dilli yönetimi ve Windows için bağımsız bir uygulama olarak dağıtımı desteklemektedir.
## Ana özellikler
- IIIF döşemelerinden otomatik görüntü yeniden yapılandırması
- Çok dilli destek (20 dil)
- Modern grafik arayüz (Qt)
- Bağımsız EXE oluşturucu ve çok dilli yükleyici
## Kurulum
1. ATK-Pro-Setup-v2.0.exe yükleyicisini veya ATK-Pro.exe bağımsız çalıştırılabilir dosyasını sürüm bölümünden indirin.
1. Kurulumu tamamlamak için ekrandaki talimatları izleyin.
1. ATK-Pro'yu Başlat menüsünden veya kurulum klasöründen başlatın.
## Proje Yapısı
- `src/` – Ana kaynak kodu (GUI, mantık, modüller)
- `varlıklar/` – Çok dilli varlıklar (rehberler, şablonlar, kaynaklar)
- `locale/` – Her dil için .ini çeviri dosyaları
- `genel_belgeler/` – Sözlükler, genel belgeler, yol haritası
- `scriptler/` – Bakım, çeviri, doğrulama betikleri
- `tests/` – Otomatik ve kapsama testleri
- `dist/` – Çıktı derleme/kurulum programı
## Belgeler
- Tarihi ve derinlemesine belgeler artık `docs_generali/archivio/`'da arşivlenmiştir.
- Bu README ve `CHANGELOG.md` dosyası, projenin durumunu ve ana kilometre taşlarını özetlemektedir.
## Tarih ve gelişim
Proje, dijital soybilim araçlarının bir evrimi olarak, şeffaflık, tarihsel arşivleme ve uluslararası desteğe odaklanarak doğmuştur. Her kilometre taşı depoda izlenir ve belgelenir.
## Krediler
Geliştirme ve bakım: Daniele Pigoli
Katkıda bulunanlar: değişiklik günlüğüne ve sürüm notlarına bakınız
## Değişiklik Günlüğü
Projedeki ana yenilikler ve kilometre taşları için `docs_generali/CHANGELOG.md` dosyasını inceleyin.
Tarihi ayrıntılar ve tam notlar için `docs_generali/archivio/` klasörüne bakınız.

-----
## Mevcut durum
- Tüm aktif modüller doğrudan ve savunma kapsama alanıyla test edilmiştir
- Doğrulanmış modüllerde `# === Test Kapsamı ===` bloğu ile açıklama
- main.py modülü, kısmi kapsama alanına (%64) sahip olmasına rağmen, orkestrasyonel olduğu için mantıksal olarak doğrulanmıştır.
### Sonraki adımlar
- v2.1'i artımlı evrim ve güncellenmiş belgelerle hazırlayın

✍️ Daniele Pigoli tarafından düzenlenmiştir – teknik titizlik ve tarihsel belleği birleştirme amacı güdülerek.
