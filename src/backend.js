import axios from 'axios'

let $axios = axios.create({
  baseURL: '/api/',
  timeout: 5000,
  headers: {'Content-Type': 'application/json'}
})

// Request Interceptor
$axios.interceptors.request.use(function (config) {
  config.headers['Authorization'] = 'Fake Token'
  return config
})

// Response Interceptor to handle and log errors
$axios.interceptors.response.use(function (response) {
  return response
}, function (error) {
  // Handle Error
  console.log(error)
  return Promise.reject(error)
})

export default {

  fetchResults (ticketType, season, workday, intercept) {
    return $axios.get(`price-elasticity/roots/${ticketType}/${season}/${workday}/${intercept}`,
      {timeout: 0})
      .then(response => response.data)
      .catch(error => {
        console.log(error.message)
      })
  },
  getTicketTypes () {
    return $axios.get(`price-elasticity/ticket-types`)
      .then(response => response.data)
      .catch(error => {
        console.log(error.message)
      })
  },
  getConfig () {
    return $axios.get(`price-elasticity/config`)
      .then(response => response.data.message)
      .catch(error => {
        console.log(error.message)
      })
  },
  postConfig (body) {
    return $axios.post(`price-elasticity/config`, body)
      .then(response => response.data)
      .catch(error => {
        console.log(error.message)
      })
  }
}
