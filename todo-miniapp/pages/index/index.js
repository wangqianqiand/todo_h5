Page({
  data: {
    todos: [],
    inputValue: ''
  },

  onLoad() {
    this.loadTodos()
  },

  // 加载本地存储的待办
  loadTodos() {
    const todos = wx.getStorageSync('todos') || []
    this.setData({ todos })
    this.updateStats()
  },

  // 保存到本地存储
  saveTodos(todos) {
    wx.setStorageSync('todos', todos)
    this.updateStats()
  },

  // 输入事件
  onInput(e) {
    this.setData({
      inputValue: e.detail.value
    })
  },

  // 添加待办
  addTodo() {
    const text = this.data.inputValue.trim()
    if (!text) {
      wx.showToast({
        title: '请输入内容',
        icon: 'none'
      })
      return
    }

    const todo = {
      id: Date.now(),
      text: text,
      completed: false,
      createTime: new Date().toLocaleString()
    }

    const todos = [todo, ...this.data.todos]
    this.setData({
      todos: todos,
      inputValue: ''
    })
    this.saveTodos(todos)
  },

  // 切换完成状态
  toggleTodo(e) {
    const id = e.currentTarget.dataset.id
    const todos = this.data.todos.map(item => {
      if (item.id === id) {
        return { ...item, completed: !item.completed }
      }
      return item
    })
    this.setData({ todos })
    this.saveTodos(todos)
  },

  // 删除待办
  deleteTodo(e) {
    const id = e.currentTarget.dataset.id
    wx.showModal({
      title: '提示',
      content: '确定删除这条待办吗？',
      success: (res) => {
        if (res.confirm) {
          const todos = this.data.todos.filter(item => item.id !== id)
          this.setData({ todos })
          this.saveTodos(todos)
        }
      }
    })
  },

  // 清除已完成
  clearCompleted() {
    wx.showModal({
      title: '提示',
      content: '确定清除所有已完成的待办吗？',
      success: (res) => {
        if (res.confirm) {
          const todos = this.data.todos.filter(item => !item.completed)
          this.setData({ todos })
          this.saveTodos(todos)
          wx.showToast({
            title: '清除成功',
            icon: 'success'
          })
        }
      }
    })
  },

  // 更新统计
  updateStats() {
    const completedCount = this.data.todos.filter(item => item.completed).length
    this.setData({ completedCount })
  }
})
