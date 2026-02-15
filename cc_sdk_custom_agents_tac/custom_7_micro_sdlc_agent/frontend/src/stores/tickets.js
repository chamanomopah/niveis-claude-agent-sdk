import { defineStore } from 'pinia'
import axios from 'axios'

const API_URL = 'http://127.0.0.1:8001'
const WS_URL = 'ws://127.0.0.1:8001/ws'

export const useTicketsStore = defineStore('tickets', {
  state: () => ({
    tickets: [],
    sessionInfo: null,
    wsConnection: null,
    isConnected: false
  }),

  getters: {
    ticketsByStage: (state) => {
      const stages = ['idle', 'plan', 'build', 'review', 'shipped', 'errored', 'archived']
      const grouped = {}

      stages.forEach(stage => {
        grouped[stage] = state.tickets.filter(t => t.stage === stage)
      })

      return grouped
    },

    getTicketById: (state) => (id) => {
      return state.tickets.find(t => t.id === id)
    }
  },

  actions: {
    async fetchTickets() {
      try {
        const response = await axios.get(`${API_URL}/tickets`)
        this.tickets = response.data
      } catch (error) {
        console.error('Failed to fetch tickets:', error)
      }
    },

    async fetchSessionInfo() {
      try {
        const response = await axios.get(`${API_URL}/session`)
        this.sessionInfo = response.data
      } catch (error) {
        console.error('Failed to fetch session info:', error)
      }
    },

    async createTicket(ticketData) {
      try {
        const response = await axios.post(`${API_URL}/tickets`, ticketData)
        // Don't push here - let WebSocket handle it to avoid duplicates
        // The WebSocket message will arrive with the ticket_created event
        return response.data
      } catch (error) {
        console.error('Failed to create ticket:', error)
        throw error
      }
    },

    async updateTicketStage(ticketId, newStage) {
      try {
        await axios.put(`${API_URL}/tickets/${ticketId}/stage`, { stage: newStage })

        // Update local state
        const ticket = this.tickets.find(t => t.id === ticketId)
        if (ticket) {
          ticket.stage = newStage
        }
      } catch (error) {
        console.error('Failed to update ticket stage:', error)
        throw error
      }
    },

    connectWebSocket() {
      if (this.wsConnection) {
        return
      }

      this.wsConnection = new WebSocket(WS_URL)

      this.wsConnection.onopen = () => {
        console.log('WebSocket connected')
        this.isConnected = true
      }

      this.wsConnection.onmessage = (event) => {
        const data = JSON.parse(event.data)
        this.handleWebSocketMessage(data)
      }

      this.wsConnection.onclose = () => {
        console.log('WebSocket disconnected')
        this.isConnected = false
        this.wsConnection = null

        // Reconnect after 3 seconds
        setTimeout(() => this.connectWebSocket(), 3000)
      }

      this.wsConnection.onerror = (error) => {
        console.error('WebSocket error:', error)
      }
    },

    handleWebSocketMessage(data) {
      switch (data.type) {
        case 'ticket_created':
          // Check if ticket already exists to prevent duplicates
          const existingTicket = this.tickets.find(t => t.id === data.ticket.id)
          if (!existingTicket) {
            this.tickets.push(data.ticket)
          }
          break

        case 'stage_updated':
          const ticket = this.tickets.find(t => t.id === data.ticket_id)
          if (ticket) {
            ticket.stage = data.new_stage
          }
          break

        case 'agent_message':
          const msgTicket = this.tickets.find(t => t.id === data.ticket_id)
          if (msgTicket) {
            if (!msgTicket.agent_messages) {
              msgTicket.agent_messages = []
            }
            msgTicket.agent_messages.push(data.message)

            // Update counts for real-time display
            if (data.counts) {
              Object.assign(msgTicket, data.counts)
            }
          }
          break

        case 'workflow_started':
        case 'workflow_completed':
        case 'workflow_error':
          // Refresh the ticket to get latest data
          this.fetchTickets()
          break
      }
    },

    disconnectWebSocket() {
      if (this.wsConnection) {
        this.wsConnection.close()
        this.wsConnection = null
        this.isConnected = false
      }
    }
  }
})