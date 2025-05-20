# Model References

## Vehicle Detection and Classification

**Models Used:** Detic, YOLO-World, YOLO3D

**Implementation:** We first use Detic for basic vehicle identification, then branch that output into two parallel processes. The first branch uses YOLO-World on cropped vehicle images based on the bounding box output of Detic to classify them as 'Sedan', 'SUV', 'truck', 'pickup truck', 'Motorcycle', or 'van'. The second branch feeds detections to YOLO3D to generate the 3D bounding boxes and get the vehicle orientation details.

**Citations:**
-  X. Zhou, V. Koltun, and P. Krähenbühl, "Detic: Detecting Twenty-thousand Classes Using Image-level Supervision," in *Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.*, 2022, pp. 10883-10893.
- T. Cheng, L. Song, Y. Ge, W. Liu, X. Wang, and Y. Shan, "YOLO-World: Real-Time Open-Vocabulary Object Detection," arXiv preprint arXiv:2401.17270, 2024.
- A. Mousavian, D. Anguelov, J. Flynn, and J. Kosecka, "3D Bounding Box Estimation Using Deep Learning and Geometry," arXiv preprint arXiv:1612.00496, Dec. 2016.

## Road Element Detection

**Models Used:** Detic

**Implementation:** We used Detic for detecting road elements such as traffic cones/cylinders and trashcans, leveraging its extensive vocabulary and effective detection capabilities.

**Citation:**
 -X. Zhou, V. Koltun, and P. Krähenbühl, "Detic: Detecting Twenty-thousand Classes Using Image-level Supervision," in *Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.*, 2022, pp. 10883-10893.

## Traffic Light Detection and Analysis

**Models Used:** Detic followed by custom processing.

**Implementation :** Detic identifies traffic lights in the scene, then the pipeline crops the image around detected bounding boxes for further processing to identify both the arrow orientation (if present) and the color state of the traffic light.

**Citation:**
-X. Zhou, V. Koltun, and P. Krähenbühl, "Detic: Detecting Twenty-thousand Classes Using Image-level Supervision," in *Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.*, 2022, pp. 10883-10893.

## Road Sign Detection

**Models Used:** YOLO-World followed by custom processing.

**Implementation:**  We used YOLO-World to detect stop signs and speed limit signs, followed by OCR processing on the cropped sign images to extract numerical speed limit values from detected signs.

**Citation:**
- T. Cheng, L. Song, Y. Ge, W. Liu, X. Wang, and Y. Shan, "YOLO-World: Real-Time Open-Vocabulary Object Detection," arXiv preprint arXiv:2401.17270, 2024.

## Lane and Road Marking Detection

**Models Used:** Mask R-CNN with geometric post-processing

**Implementation:** We used mask R-CNN which provides pixel-level segmentation for lane markings and directional arrows on the road. Then we applied additional geometric methods to the segmentation masks for accurate arrow orientation classification.

**Citation:**
- K. He, G. Gkioxari, P. Dollár, and R. Girshick, "Mask R-CNN," in Proceedings of the IEEE International Conference on Computer Vision (ICCV), pp. 2961-2969, Oct. 2017.

## Pedestrian Pose Detection

**Models Used:** OSX 

**Implementation**: We used OSX for pedestrian detection, it enabled comprehensive 3D human body, mesh recovery from a single image. 

**Citation:**

- J. Lin, A. Zeng, H. Wang, L. Zhang, and Y. Li, "One-Stage 3D Whole-Body Mesh Recovery with Component Aware Transformer," in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), pp. 21159-21168, 2023.


## Stop Sign, speed limit sign Detection

**Models Used:** YOLO-World (yolov8x-worldv2.pt) with OCR

**Implementation** : We used the yolov8 worldv2 model from YOLO-World for detecting the stop signs and speed limit signs. After detecting the speed limit sign (which is classified as road sign only), we applied OCR processing on the cropped sign images to extract numerical speed limit values from detected signs to make sure it is a speed limit sign itself.

**Citation:**

- T. Cheng, L. Song, Y. Ge, W. Liu, X. Wang, and Y. Shan, "YOLO-World: Real-Time Open-Vocabulary Object Detection," arXiv preprint arXiv:2401.17270, 2024.



## Links

**Detic:** https://github.com/facebookresearch/Detic

**OSX:** https://github.com/IDEA-Research/OSX

**YOLO3D:** https://github.com/ruhyadi/YOLO3D

**YOLO-World:** https://docs.ultralytics.com/models/yolo-world/

**Mask R-CNN:** https://debuggercafe.com/lane-detection-using-mask-rcnn/

**Yolo World V8:**https://docs.ultralytics.com/models/yolo-world/#available-models-supported-tasks-and-operating-modes