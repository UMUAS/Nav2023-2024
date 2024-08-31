import cv2 as cv

# from models.common import DetectMultiBackend
# from utils.general import non_max_suppression, scale_coords
# from utils.torch_utils import select_device
# from utils.augmentations import letterbox
import torch
import yolov5

# device = select_device('')
# model = DetectMultiBackend('yolo5s.pt', device=device, dnn=False)
# model.warmup(imgsz=(1, 3, 640, 640), half=False)

# train = "../train/images"
# test = "../test/images"
# valid = "../valid/images"


# def predict(img):
#     with torch.no_grad():
#         img = letterbox(img, 640)[0]
#         img = img[:, :, ::-1].transpose(2, 0, 1)
#         img = np.ascontiguousarray(img)
#         img = torch.from_numpy(img).to(device)
#         img = img.half() if model.half else img.float()
#         img /= 255.0
#         if img.ndimension() == 3:
#             img = img.unsqueeze(0)
#         pred = model(img, augment=False)[0]
#         pred = non_max_suppression(pred, 0.4, 0.5, classes=None, agnostic=False)
#         return pred


# def get_boxes(img):
#     pred = predict(img)
#     boxes = []
#     for i, det in enumerate(pred):
#         if det is not None and len(det):
#             det[:, :4] = scale_coords(img.shape[2:], det[:, :4], img.shape).round()
#             for *xyxy, conf, cls in reversed(det):
#                 boxes.append(xyxy)
#     return boxes


model = yolov5.load("./yolov5s.pt")
# model = model.fuse() # Fuse parameters to improve inference performance

cap = cv.VideoCapture("../../../DJI_0071.MP4")

while cap.isOpened():
    ret, frame = cap.read()

    if not ret:
        break

    frame = cv.resize(frame, fx=0.5, fy=0.5, dsize=(0, 0))
    img = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

    # run inference
    with torch.no_grad():
        pred = model(img)

    # process detections
    # parse results
    predictions = pred.pred[0]
    boxes = predictions[:, :4]  # x1, y1, x2, y2
    scores = predictions[:, 4]
    categories = predictions[:, 5]
    # draw boxes
    for box in boxes:
        x1, y1, x2, y2 = box
        cv.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        cv.putText(
            frame,
            "landing_pad",
            (int(x1), int(y1)),
            cv.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
            cv.LINE_AA,
        )
        # randint = torch.randint(0, 1000, (1,)).item()
        # cv.imwrite(f'./detections/img_{randint}.png', frame)
        # print(f'./detections/img_{randint}.png')

    cv.imshow("frame", frame)
    if cv.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv.destroyAllWindows()
