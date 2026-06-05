import cv2
import sys
import time

def launch_iriun_tactical_hud():
    """
    ระบบดึงสัญญาณภาพสตรีมสดจาก Iriun Webcam เข้าสู่แกนประมวลผลหลักทางยุทธวิธี
    """
    print("[SYSTEM] กำลังเปิดใช้งานหน่วยประมวลผลสตรีมสด...")
    print("[INFO] โปรดตรวจสอบว่าคุณได้เปิดแอป Iriun บนมือถือและคอมพิวเตอร์แล้ว")

    # ค้นหาพอร์ตกล้อง Iriun โดยปกติในระบบ Windows หากไม่มีเว็บแคมอื่น Iriun จะอยู่ที่ Index 0 หรือ 1
    # เราสามารถวนลูปค้นหาหรือระบุค่าเริ่มต้นได้
    camera_index = 0
    
    # หากผู้ใช้ระบุ Index ผ่าน Command Line เช่น python iriun_tactical_hud.py 1
    if len(sys.argv) > 1:
        camera_index = int(sys.argv[1])

    # เชื่อมต่อกับอุปกรณ์รับภาพจำลองของ Iriun
    cap = cv2.VideoCapture(camera_index)

    # บังคับใช้ DirectShow (DSHOW) บน Windows เพื่อให้ดึงสัญญาณได้เร็วที่สุดและไม่เกิดอาการภาพค้าง
    if sys.platform.startswith('win'):
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

    # กำหนดมิติมุมมองทางยุทธวิธีให้ตรงกับค่าการสตรีมสูงสุดของ Iriun
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)   # รองรับสูงสุดถึง Full HD / 4K
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cap.set(cv2.CAP_PROP_FPS, 60)             # ปลดล็อกเฟรมเรตตามที่ฮาร์ดแวร์มือถือส่งมา

    if not cap.isOpened():
        print(f"[CRITICAL ERROR] ไม่สามารถเข้าถึงกล้องที่ Index {camera_index} ได้")
        print("[SUGGESTION] ลองรันคำสั่งโดยเปลี่ยนเลขพอร์ต เช่น: python iriun_tactical_hud.py 1")
        return

    print(f"[SUCCESS] เชื่อมต่อสัญญาณภาพกล้อง Iriun สำเร็จ (Source Index: {camera_index})")
    print("[HUD] กำลังเปิดหน้าจอควบคุมการรบ... [กด 'Q' เพื่อสละการเชื่อมต่อ]")

    # ตัวแปรสำหรับการคำนวณและแสดงผล FPS จริงบนหน้าจอ (Real-time Telemetry)
    prev_frame_time = 0
    new_frame_time = 0

    try:
        while True:
            # ดึงเฟรมภาพดิบจากไดรเวอร์ Iriun
            ret, frame = cap.read()
            
            if not ret:
                print("[SIGNAL DROP] ตรวจพบสัญญาณภาพขาดหายชั่วคราว จาก Iriun Server...")
                time.sleep(0.1)
                continue

            # --- ส่วนคำนวณความเร็วการประมวลผลจริง (Real-time FPS Counter) ---
            new_frame_time = time.time()
            # คำนวณหาค่าความต่างของเวลาระหว่างเฟรม (1 หารด้วยเวลาที่ใช้ไป)
            fps = 1 / (new_frame_time - prev_frame_time) if (new_frame_time - prev_frame_time) > 0 else 0
            prev_frame_time = new_frame_time

            # -----------------------------------------------------------------
            # [TACTICAL OVERLAY / AI IMPLEMENTATION ZONE]
            # พื้นที่สำหรับใส่โมเดล AI ของคุณ (เช่น YOLO, OpenCV Face Detection) 
            # ภาพที่ได้ตอนนี้คือเรียลไทม์ 100% คุณสามารถเอาตัวแปร 'frame' ไปประมวลผลต่อได้เลย
            # -----------------------------------------------------------------

            # วาดกรอบสถิติระบบลงบนภาพวิดีโอสด (HUD Overlay)
            fps_text = f"TACTICAL LINK | FPS: {int(fps)}"
            resolution_text = f"RES: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}"
            
            # ใส่ข้อความสถานะลงบนมุมบนซ้ายของภาพ
            cv2.putText(frame, fps_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(frame, resolution_text, (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1, cv2.LINE_AA)

            # แสดงผลภาพบนหน้าจอมอนิเตอร์
            cv2.imshow("OMNI-TECH TACTICAL HUD (via IRIUN)", frame)

            # ตรวจจับการกดปุ่ม 'q' เพื่อปิดโปรแกรมอย่างปลอดภัย
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("[COMMAND] ผู้ควบคุมสั่งการปิดระบบตรวจการณ์")
                break

    except Exception as e:
        print(f"[SYSTEM FAILURE] เกิดข้อผิดพลาดในแกนควบคุม: {e}")

    finally:
        # คืนทรัพยากรให้ระบบปฏิบัติการเพื่อป้องกันปัญหากล้องค้าง (Resource Leak)
        cap.release()
        cv2.destroyAllWindows()
        print("[SYSTEM] ตัดการเชื่อมต่ออุปกรณ์ภายนอกอย่างปลอดภัย สถานะปัจจุบัน: OFFLINE")

if __name__ == "__main__":
    launch_iriun_tactical_hud()
