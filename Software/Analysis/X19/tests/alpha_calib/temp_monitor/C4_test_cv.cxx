#include<opencv2/opencv.hpp>
using namespace cv;
int main()
{
    VideoCapture webcam;
    webcam.open(0);
    Mat frame;

    webcam >> frame;
//     imshow("My Webcam",frame);

    imwrite("webcam_capture.jpg", frame);
    webcam.release();
    return 0;
}
