# 物业管理系统开发经验

## 项目信息
- **名称**: property-management-system
- **GitHub**: github.com/18suideDaxian/property-manager
- **开发日期**: 2026-04-20 启动，2026-04-27 完成全栈开发
- **技术栈**: Spring Boot 3.x + MyBatis Plus + Vue 3 + Element Plus + uni-app + uView UI + MySQL 8.0

## 功能模块

### 业主端（微信小程序）
- 手机号注册/登录
- 缴费（水费、电费、物业费、停车费）
- 报修（5种类型：水电/门窗/家电/管道/其他，支持拍照+预约日期）
- 公告查看
- 家业管理（绑定房产信息）
- 个人中心（我的家业/缴费/报修/修改名称）

### 管理员端（Web 后台）
- 超级管理员内部添加，普通管理员注册后分配权限
- 用户管理（增删改查业主）
- 楼盘管理（小区管理、Excel 导入导出房产资源）
- 缴费管理（账单查看、费用设置、收款操作）
- 报修工单（查看/处理/分配工单，工单流转）
- 公告管理（发布/编辑/删除）
- 系统设置（账号管理、角色权限、操作日志）

### 后端（Spring Boot）
- JWT 认证 + Spring Security
- MyBatis Plus + LambdaQueryWrapper
- 16 个实体类 + 16 个 Mapper + 6 个 Service + 11 个 Controller
- Knife4j API 文档

## 开发方式
- 使用 Sub Agent 并行开发（后端 + 管理员端 + 业主端）
- 分 4 批次完成：后端业务模块 → 管理员端 → 业主端 → 部署配置/文档
- 每批次完成后推送到 GitHub

## 部署
- Docker Compose 一键部署（MySQL + Redis + 后端 + Nginx）
- 超级管理员默认账号：admin / admin123

## 经验总结
- 大型项目分模块并行开发效率高
- Sub Agent 最多同时 spawn 2 个，避免资源竞争
- 每完成一个模块立即 git add + commit + push，避免丢失
- 前后端分离部署，Nginx 反向代理后端 API
