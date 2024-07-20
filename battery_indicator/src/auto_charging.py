import rospy
import yaml
from battery_indicator.msg import ErrorStatus,BatteryStatus
from std_srvs.srv import SetBool

class BatteryAuto:
    def __init__(self):
        yaml_file="/home/myubuntu/ros-training/src/battery_indicator/config/param_battery.yaml"
        with open(yaml_file, 'r') as f:
            config = yaml.safe_load(f)
        self.critical_percent = rospy.get_param('~critical_percent', 5)
        self.full_battery = rospy.get_param('~full_battery', 100)
        self.warning_percentage = rospy.get_param('~warning_percentage', 20)
        self.error_msg = False
        self.error_publisher=rospy.Publisher('error_status',ErrorStatus,queue_size=10)
        self.sub = rospy.Subscriber('battery_status',BatteryStatus,self.Status)
        self.plug_cable_client = rospy.ServiceProxy('/plug_cable', SetBool)
    
    def Status(self,msg):
        if msg.batteryPercentage < self.critical_percent:
            self.handle_plug_cable(True)
        elif msg.batteryPercentage >= self.full_battery:
            self.handle_plug_cable(False)
        
        if msg.batteryPercentage < self.warning_percentage:
            self.error_msg = True
            self.publish_errorstatus()
        else:
            rospy.loginfo("Battery Sufficient")
    def handle_plug_cable(self, plug):
        try:
            # Call the /plug_cable service with plug parameter
            response = self.plug_cable_client(plug)
            rospy.loginfo("Service response: %s", response.message)
        except rospy.ServiceException as e:
            rospy.logerr("Service call failed: %s", e)

    def publish_errorstatus(self):
        msg=ErrorStatus()
        msg.error=self.error_msg
        msg.description = "Robot is about to deplete its battery, don't assign new job."
        if(msg.error): 
            self.error_publisher.publish(msg)
        self.error_msg=False
    
if __name__ == '__main__':
    rospy.init_node('battery_auto')
    ba = BatteryAuto()
    rospy.spin()
