<template>
  <div>
    <h5>Тут вы можете загрузить новый файл</h5>
    <h6>Важно! Структура файла должна быть:</h6>
    <p>Тип билета (текст)</p>
    <p>Дата (формат: ДД/ММ/ГГГГ)</p>
    <p>Цена (формат: ХХХХ.ХХ)</p>
    <p>Количество билетов (формат: ХХХХ)</p>
    <p>Вы можете поменять именя колонок во вкладке Config</p>

    <form action="#">
      <div class="file-field input-field">
        <div class="btn">
          <span>File</span>
          <input type="file" id="file">
        </div>
        <div class="file-path-wrapper">
          <input class="file-path validate" type="text">
        </div>
      </div>
    </form>
    <button class="btn" @click='postNewFile()'>Загрузить</button>
    <div id="result"></div>
  </div>
</template>

<script>
export default {
  methods: {
    postNewFile () {
      // !TODO move the request logic to @backend
      let file = document.querySelector('#file').files[0]
      let formData = new FormData()

      formData.append('file', file)
      fetch('/api/price-elasticity/data', {
        method: 'POST',
        body: formData
      }).then(response => {
        console.log(response)
        if (response.ok) {
          document.querySelector('#result').innerHTML = '<h5>Готово!</5>'
        }
      })
    }
  }
}
</script>

<style lang="scss" scoped>
</style>
