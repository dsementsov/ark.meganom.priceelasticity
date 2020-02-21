<template>
    <div>
        <h5>Тут вы можете загрузить новый файл</h5>
        <h6>Важно! Структура файла должна быть:</h6>
        <p>Тип билета (текст)</p>
        <p>Дата (формат: ДД/ММ/ГГГГ)</p>
        <p>Цена (формат: ХХХХ.ХХ)</p>
        <p>Количество билетов (формат: ХХХХ)</p>

         <form action="/api/price-elasticity/data" method="post">
            <div class="file-field input-field">
                <div class="btn">
                    <span>Выбрать файл</span>
                    <input type="file">
                </div>
                <div class="file-path-wrapper">
                    <input class="file-path validate" type="text">
                </div>
            </div>
            <div>
                <button type="submit" class="btn">Загрузить</button>
            </div>
        </form>
    </div>
</template>

<script>
export default {

}
</script>

<style lang="scss" scoped>

</style>
