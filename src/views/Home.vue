<template>
  <div class="home">
    <div id="config">
      <div class="input-field col s12">
        <select id="config_ticket_type" required>
          <option value disabled selected>Выбрать тип билета</option>
          <option value="all">Все</option>
          <option v-for="item in ticketTypes" :value="item" :key="item">{{ item }}</option>
        </select>
        <label>Тип билета</label>
      </div>
      <div class="input-field col s12">
        <select id="config_season" required>
          <option value="null" disabled selected>Выбрать сезон</option>
          <option value="all">Все</option>
          <option value="high">Высокий</option>
          <option value="mid">Средний</option>
          <option value="low">Низкий</option>
        </select>
        <label>Сезон</label>
      </div>
      <div class="input-field col s12">
        <select id="config_workday" required>
          <option value disabled selected>Выбрать день</option>
          <option value="all">Все</option>
          <option value="1">Рабочий день</option>
          <option value="0">Выходной</option>
        </select>
        <label>Тип дня</label>
      </div>
      <div class="input-field col s12">
        <select id="config_intercept" required>
          <option value disabled>Включить интерцепт</option>
          <option value="1" selected>Да - Рекомендовано</option>
          <option value="0">Нет</option>
        </select>
        <label>Интерцепт</label>
      </div>
      <div></div>
      <div class="switch" @click="manualAutoSwitch()">
        <label>
          Авто
          <input type="checkbox" id="manual-auto-switch" />
          <span class="lever"></span>
          Ввести Цену / Количество
        </label>
      </div>
      <div class="row">
        <button @click="get_data()" class="btn right">Получить данные</button>
      </div>
      <div class="container left" v-if="this.advanced">
        <div class="row">
          <div class="col s4">
            <h6>Цена:</h6>
          </div>
          <div class="col s6">
            <input type="text" class="input-field" id="custom-price" />
          </div>
        </div>
        <div class="row">
          <div class="col s4">
            <h6>Количество билетов:</h6>
          </div>
          <div class="col s6">
            <input type="text" class="input-field" id="custom-quantity" />
          </div>
        </div>
      </div>
    </div>
    <div id="results" class="container"></div>
  </div>
</template>

<script>
import M from 'materialize-css'

export default {
  name: 'home',
  data () {
    return {
      advanced: false,
      s: {
        high: 'Высокий',
        mid: 'Средний',
        low: 'Низкий'
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
      fetch('/api/price-elasticity/ticket-types', {
        method: 'GET'
      })
        .then(response => {
          return response.json()
        })
        .then(tt => {
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
    manualAutoSwitch () {
      var sw = document.querySelector('#manual-auto-switch')
      if (sw == null) {
        sw = false
      } else {
        console.log(sw)
        sw = sw.checked
      }
      this.advanced = sw
    },
    get_data () {
      var ticketType = document.querySelector('#config_ticket_type').value
      var season = document.querySelector('#config_season').value
      var workday = document.querySelector('#config_workday').value
      var intercept = document.querySelector('#config_intercept').value
      var p, q
      if (this.advanced) {
        p = document.querySelector('#custom-price').value
        q = document.querySelector('#custom-quantity').value
        if (p === '') {
          p = 'all'
        }
        if (q === '') {
          q = 'all'
        }
      } else {
        p = 'all'
        q = 'all'
      }
      if (ticketType !== '' && season !== '' && workday !== '') {
        fetch(
          `/api/price-elasticity/roots/${ticketType}/${season}/${workday}/${intercept}/${p}/${q}`,
          {
            method: 'GET'
          }
        )
          .then(response => {
            return response.json()
          })
          .then(response => {
            var data = response.message
            console.log(data)
            this.displayResults('<h4>Максимизация прибыли согласно модели</h4>', true)
            for (var el in data) {
              var m = data[el]
              this.displayResults(
                this.shapeReults(
                  {
                    ticketType: m.type,
                    season: m.season,
                    workday: m.workday
                  },
                  {
                    p: m.p,
                    q: m.q,
                    r: m.adj_r
                  }
                ),
                false
              )
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
      var out =
          '<p>Тип билета: ' +
          i.ticketType +
          '</p>' +
          '<p>Сезон: ' +
          this.s[i.season] +
          '</p>' +
          '<p>Рабочий день: ' +
          this.w[i.workday] +
          '</p>' +
          '<p>Оптимальная цена: ' +
          o.p +
          '</p>' +
          '<p>Количество проданых билетов: ' +
          o.q +
          '</p>' +
          '<p>Adjusted R squared: ' +
          o.r +
          '</p>'
      return out
    }
  }
}
</script>

<style lang="scss"></style>
