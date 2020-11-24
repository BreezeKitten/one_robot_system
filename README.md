# one_robot_system

# 如果你在windows上使用 請換到master分支(git checkout master)

# 以下幾個檔案在TX2中使用

Main_process.py:

  主程式，注意檔案中的IS_ROS = True
  
Navigation_core.py:
  
  導航網路運算核心，Main_process會透過socket將狀態資料傳進此處
  
  再回傳速度與角速度命令

# 以下幾個檔案在NUC中使用

all_robot_publisher.py & FB_all_robot_publisher.py:
  
  此兩個檔案作用相同，差別在訂閱/cmd_vel或/FeedBack_Vel
  
  前者在gazebo中使用；後者在實驗中使用
  
  在各TX2的Main_process透過socket訂閱後，可發布全機器人狀態給各TX2
  
ros_pub_tool.py:
  
  此檔案用於在模擬或實驗中的操作介面
