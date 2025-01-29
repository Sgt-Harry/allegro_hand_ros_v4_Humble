from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    # 1) 声明可选参数
    declared_arguments = []
    declared_arguments.append(
        DeclareLaunchArgument(
            "chirality",
            default_value="right",
            description="Chirality (left/right) of the Allegro hand."
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "parent",
            default_value="map",
            description="The link with which the hand attach."
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "prefix",
            default_value="allegro",
            description="Prefix for the Allegro hand joint names."
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "ur5_attachment",
            default_value="false",
            description="If true, the Allegro hand is attached to a UR5. Otherwise it's standalone."
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "desk_stand",
            default_value="true",
            description="If true, the Allegro hand is placed on a desk stand."
        )
    )

    # 2) 取出参数值
    chirality = LaunchConfiguration("chirality")
    parent = LaunchConfiguration("parent")
    prefix = LaunchConfiguration("prefix")
    ur5_attachment = LaunchConfiguration("ur5_attachment")
    desk_stand = LaunchConfiguration("desk_stand")

    # 3) 指定主 Xacro 文件 (可根据你自己的文件名和目录调整)
    #    假设你在 allegro_hand_description/urdf/ 下放置了 allegro_hand_main.urdf.xacro
    xacro_file = PathJoinSubstitution([
        FindPackageShare("allegro_hand_description"),
        "urdf",
        "allegro_hand_main.xacro"
    ])

    # 4) 通过 Command + xacro 生成机器人描述 (URDF)
    robot_description_content = Command([
        PathJoinSubstitution([FindExecutable(name="xacro")]),
        " ",
        xacro_file,
        " ",
        "chirality:=", chirality, 
        " ",
        "parent:=", parent, 
        " ",
        "prefix:=", prefix,
        " ",
        "ur5_attachment:=", ur5_attachment,
        " ",
        "desk_stand:=", desk_stand
    ])
    # 转换成 robot_description (供 robot_state_publisher 节点使用)
    robot_description = {
        "robot_description": ParameterValue(robot_description_content, value_type=str)
    }

    # 5) 如果你有自定义的 RViz 配置文件，可以放在 allegro_hand_description/rviz/ 下
    #    下面就假设有一个叫 "allegro_hand.rviz"
    rviz_config_file = PathJoinSubstitution([
        FindPackageShare("allegro_hand_description"),
        "rviz",
        "view_hand.rviz"
    ])

    # 6) 定义要启动的节点

    joint_state_publisher_node = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui"
    )

    # robot_state_publisher，根据 robot_description 发布 TF
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="both",
        parameters=[robot_description],
    )

    # RViz，用于可视化
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="log",
        arguments=["-d", rviz_config_file],
    )

    # 7) 将节点聚合并返回 LaunchDescription
    nodes_to_start = [
        joint_state_publisher_node,
        robot_state_publisher_node,
        rviz_node,
    ]
    return LaunchDescription(declared_arguments + nodes_to_start)
