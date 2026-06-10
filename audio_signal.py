import pyaudio
import numpy as np
import time

# --- ตั้งค่าการดักจับสัญญาณเสียงจากลำโพง ---
CHUNK = 1024               # ขนาดบล็อกเสียง (ยิ่งน้อยยิ่งเรียลไทม์ แต่ใช้บิตเรตสูง)
FORMAT = pyaudio.paInt16    # รูปแบบสัญญาณเสียง 16-bit
CHANNELS = 1                # ดักฟังแบบ Mono Channel
RATE = 44100                # ความถี่เสียงมาตรฐาน

p = pyaudio.PyAudio()

# เปิด Stream ดักจับสัญญาณเสียง (ต้องเปิด Stereo Mix บน Windows เพื่อดักเสียงลำโพง)
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("🚀 ระบบเริ่มส่งสัญญาณจังหวะแล้ว... (กด Ctrl+C เพื่อหยุด)")

smooth_signal = 0.0

try:
    while True:
        # 1. อ่านข้อมูลเสียงดิบจากระบบ
        data = stream.read(CHUNK, exception_on_overflow=False)
        audio_data = np.frombuffer(data, dtype=np.int16)
        
        # 2. คำนวณหาค่าความดังเฉลี่ย (Root Mean Square)
        rms = np.sqrt(np.mean(audio_data**2)) if len(audio_data) > 0 else 0
        
        # 3. แปลงค่าความดังให้เป็น สัญญาณจังหวะ (Pulse Signal) ช่วง 0.0 ถึง 1.0
        # ปรับตัวหาร (4000.0) ตามความดังของคอมพิวเตอร์คุณ ยิ่งน้อยสัญญาณยิ่งไว
        target_signal = rms / 4000.0 
        
        # ควบคุมไม่ให้ค่าเกิน 1.0
        if target_signal > 1.0:
            target_signal = 1.0
            
        # 4. ทำให้สัญญาณนิ่งและสมูทขึ้น ไม่กระชากเกินไป
        smooth_signal += (target_signal - smooth_signal) * 0.4
        
        # ตรวจสอบค่ากรณีเสียงเงียบสนิท
        if smooth_signal < 0.01:
            smooth_signal = 0.0

        # 5. แสดงผลสัญญาณออกมาเป็นตัวเลข หรือจะนำตัวแปรนี้ไปส่งต่อ (Emit) ก็ได้
        # ตัวอย่าง: แสดงเป็นแถบพลังงานใน Terminal เพื่อดูจังหวะ
        bar = "█" * int(smooth_signal * 40)
        print(f"Signal Output: {smooth_signal:.2f} | {bar:<40}", end="\r")
        
        # หน่วงเวลาเล็กน้อยเพื่อให้ระบบไม่ทำงานหนักเกินไป (ประมาณ 60Hz)
        time.sleep(0.016)

except KeyboardInterrupt:
    print("\n🛑 หยุดการส่งสัญญาณเสียง")

# เคลียร์ระบบเสียงเมื่อปิดโปรแกรม
stream.stop_stream()
stream.close()
p.terminate()
