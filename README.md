# أيقونات 3D واقعية لبوستات باقات بوت مواعيد العيادات

تصميم وتطوير: **المهندس إبراهيم فهيم**

المستودع ده بيرسم أيقونة واقعية لكل نوع تحليل (سكر، كلى، كبد، غدة درقية...) بنفس ستايل فولدر B،
والبوت بيستخدمها في بوست الباقة.

## مفتاح الرسم (مرة واحدة — مجاني)

**Cloudflare Workers AI** (موديل FLUX، مجاني لحد مئات الصور في اليوم):
1. اعمل حساب مجاني على https://dash.cloudflare.com/sign-up
2. **Account ID**: من https://dash.cloudflare.com ← أي صفحة ← على اليمين «Account ID» ← Copy.
3. **API Token**: https://dash.cloudflare.com/profile/api-tokens ← Create Token ← قالب **Workers AI** ← Use template ← Continue ← Create ← Copy.
4. في المستودع: **Settings ← Secrets and variables ← Actions ← New repository secret**:
   - `CF_ACCOUNT_ID` = الـ Account ID
   - `CF_API_TOKEN` = الـ Token

(اختياري) `GEMINI_API_KEY` من https://aistudio.google.com/apikey — لو موجود بيستخدمه الأول.

## التشغيل

- **Actions ← Generate icons ← Run workflow** — بعد كام دقيقة الصور في `icons/` والمعاينة في `preview.jpg`.
- صورة معينة تتعاد بشكل تاني؟ اكتب اسمها في **only** وغيّر **seed**.
- تحليل جديد؟ ضيف سطر في `subjects.json` (`"الاسم": "وصف بالإنجليزي"`) والرسم بيشتغل لوحده.

## في البوت

صور `icons/*.jpg` بتتحط في فولدر `icons` جوه فولدر بيانات البوت، وبتتستخدم في البوست لوحدها.
