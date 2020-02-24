<template>
  <div class="home">
    <div id="config">
      <div class="input-field col s12">
        <select id="config_ticket_type" required>
          <option value="" disabled selected>Выбрать тип билета</option>
          <option value="all">Все</option>
          <option v-for="item in ticketTypes" :value="item" :key="item">{{item}}</option>
        </select>
        <label>Тип билета</label>
      </div>
      <div class="input-field col s12">
        <select id="config_season" required>
          <option value=null disabled selected>Выбрать сезон</option>
          <option value="all">Все</option>
          <option value="high">Высокий</option>
          <option value="mid">Средний</option>
          <option value="low">Низкий</option>
        </select>
        <label>Сезон</label>
      </div>
      <div class="input-field col s12">
        <select id="config_workday" required>
          <option value="" disabled selected>Выбрать день</option>
          <option value="all">Все</option>
          <option value="1">Рабочий день</option>
          <option value="0">Выходной</option>
        </select>
        <label>Тип дня</label>
      </div>
      <div class="input-field col s12">
        <select id="config_intercept" required>
          <option value="" disabled>Включить интерцепт</option>
          <option value=1 selected>Да - Рекомендовано</option>
          <option value=0>Нет</option>
        </select>
        <label>Интерцепт</label>
      </div>
      <div>
      </div>
    </div>
    <button @click='get_data()' class="btn right">Получить данные</button>
    <div id='results'></div>
  </div>
</template>

<script>
import $backend from '@/backend'
import M from 'materialize-css'

export default {
  name: 'home',
  data () {
    return {
      s: {
        'high': 'Высокий',
        'mid': 'Средний',
        'low': 'Низкий'
      },
      w: {
        '1': 'Да',
        '0': 'Нет'
      },
      ticketTypes: []
    }
  },
  mounted: function () {
    try {
      $backend.getTicketTypes().then(tt => {
        this.ticketTypes = tt.message
        var sel = document.querySelector('#config_ticket_type')
        for (var el in tt.message) {
          var opt = document.createElement('option')
          opt.value = tt.message[el]
          opt.text = tt.message[el]
          sel.append(opt)
        }
        var elems = document.querySelectorAll('select')
        var options = {}
        M.FormSelect.init(elems, options)
      })
    } catch (error) {
      console.log(`Problem with element ${error}`)
      var elems = document.querySelectorAll('select')
      var options = {}
      M.FormSelect.init(elems, options)
    }
  },
  methods: {
    get_data () {
      var ticketType = document.querySelector('#config_ticket_type').value
      var season = document.querySelector('#config_season').value
      var workday = document.querySelector('#config_workday').value
      var intercept = document.querySelector('#config_intercept').value
      if (ticketType !== '' && season !== '' && workday !== '') {
        $backend.fetchResults(ticketType, season, workday, intercept).then(data => {
          this.displayResults('<h4>Максимизация прибыли согласно модели</h4>', true)
          for (var el in data.message) {
            var m = data.message[el]
            this.displayResults(this.shapeReults({
              ticketType: m.type,
              season: m.season,
              workday: m.workday}, {p: m.p, q: m.q, r: m.adj_r}), false)
          }
        })
      } else {
        this.displayResults('Пожалуйста сделайте выбор!')
      }
    },
    displayResults (results, inplace) {
      var resultsContainer = document.querySelector('#results')
      if (inplace) {
        resultsContainer.innerHTML = ''
      }
      resultsContainer.innerHTML = resultsContainer.innerHTML + '<br>' + results
    },
    shapeReults (i, o) {
      var out = '<p>Тип билета: ' + i.ticketType + '</p>' +
                  '<p>Сезон: ' + this.s[i.season] + '</p>' +
                  '<p>Рабочий день: ' + this.w[i.workday] + '</p>' +
                  '<p>Оптимальная цена: ' + o.p + '</p>' +
                  '<p>Количество проданых билетов: ' + o.q + '</p>' +
                  '<p>Adjusted R squared: ' + o.r + '</p>'
      return out
    }
  }
}
</script>

<style lang="scss">

</style>
