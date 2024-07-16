import onnxruntime
from . import utils

class YOLOv8:

    def __init__(self, model_path, device="cpu"):
        if device == 'cpu':
            providers = ['CPUExecutionProvider']
        elif device == 'gpu':
            providers = ['CUDAExecutionProvider']
        else:
            assert False, f'Device {device} is not available.'

        self.session = onnxruntime.InferenceSession(model_path, providers=providers)


    def __call__(self, img, size=640, conf_thres=0.7, iou_thres=0.5):
        # prepare input
        inp, orig_size, scaled_size = utils.prepare_input(img, size)

        # Perform inference on the image
        outp = self.inference(inp)

        # post-process
        boxes, scores, class_ids = utils.post_process(outp, conf_thres=conf_thres, iou_thres=iou_thres)

        # resize boxes
        boxes = utils.scale_boxes(boxes, orig_size, scaled_size)

        # parse detections
        detections = utils.parse_detections(boxes, scores, class_ids)

        return detections

    def inference(self, input_tensor):
        outputs = self.session.run(['output0'], {'images': input_tensor})
        return outputs
    
class YOLOv8Pose(YOLOv8):

    def __call__(self, img, size=640, conf_thres=0.7, iou_thres=0.5):
        # prepare input
        inp, orig_size, scaled_size = utils.prepare_input(img, size)

        # Perform inference on the image
        outp = self.inference(inp)

        # post-process
        boxes, scores, class_ids, kps = utils.post_process_pose(outp, conf_thres=conf_thres, iou_thres=iou_thres)

        # resize boxes
        boxes = utils.scale_boxes(boxes, orig_size, scaled_size)

        # resize kps
        kps = utils.scale_kps(kps, orig_size, scaled_size)

        # parse detections
        detections = utils.parse_detections_w_kps(boxes, scores, class_ids, kps)

        return detections