# one_robot_system

# 如果你在TX2或NUC上使用，請切換至TX2分支(git checkout TX2)

# 此部分的code在Windows上運行，用來測試虛擬機器人放置的部分

Main_process.py 

  主程式，注意IS_ROS = False
  
  此程式是直接import Naivgation_cor，與另一個分支不同
  
  開啟後會直接開始機器人運行
  
geo_virtual_robot.py

  虛擬機器人放置最主要邏輯的實現程式
  
  若要修改邏輯請修此檔案
  
geo_func.py

  基本幾何運算的程式
  
  應該是完成了
  
  主要使用geopandas來實現幾何運算(但效率堪憂)
  
# 測試流程

在Spyder中運行Main_process.py

然後在command line中輸入

Sim_Process(TEST_Agent, 存圖路徑)

就會開始測試

測試環境宣告在上方，Map與real_Map中，更進一步設置是放在geo_virtual_robot.py中

是利用幾何圖形設置的，如何與ROS上真正使用的地圖連結?(未完成事項)
