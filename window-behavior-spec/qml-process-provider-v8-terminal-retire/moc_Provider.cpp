/****************************************************************************
** Meta object code from reading C++ file 'Provider.hpp'
**
** Created by: The Qt Meta Object Compiler version 69 (Qt 6.11.2)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include "Provider.hpp"
#include <QtCore/qmetatype.h>

#include <QtCore/qtmochelpers.h>

#include <memory>


#include <QtCore/qxptype_traits.h>
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'Provider.hpp' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 69
#error "This file was generated using the moc from 6.11.2. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

#ifndef Q_CONSTINIT
#define Q_CONSTINIT
#endif

QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
QT_WARNING_DISABLE_GCC("-Wuseless-cast")
namespace {
struct qt_meta_tag_ZN22ObjectLifetimeProviderE_t {};
} // unnamed namespace

template <> constexpr inline auto ObjectLifetimeProvider::qt_create_metaobjectdata<qt_meta_tag_ZN22ObjectLifetimeProviderE_t>()
{
    namespace QMC = QtMocConstants;
    QtMocHelpers::StringRefStorage qt_stringData {
        "ObjectLifetimeProvider",
        "processLifecycleChanged",
        "",
        "process",
        "lease",
        "engineScope",
        "QVariantMap",
        "armProcess",
        "menu",
        "row",
        "popup",
        "out",
        "err",
        "role",
        "originalJSON",
        "actualQuickshell",
        "retireProcess",
        "QVariant",
        "processState",
        "cancelProcess",
        "observePopup",
        "QQuickItem*",
        "observe",
        "widget",
        "delegate"
    };

    QtMocHelpers::UintData qt_methods {
        // Signal 'processLifecycleChanged'
        QtMocHelpers::SignalData<void(QObject *, qulonglong)>(1, 2, QMC::AccessPublic, QMetaType::Void, {{
            { QMetaType::QObjectStar, 3 }, { QMetaType::ULongLong, 4 },
        }}),
        // Method 'engineScope'
        QtMocHelpers::MethodData<QVariantMap()>(5, 2, QMC::AccessPublic, 0x80000000 | 6),
        // Method 'armProcess'
        QtMocHelpers::MethodData<QVariantMap(QObject *, QObject *, QObject *, QObject *, QObject *, QObject *, const QString &, const QString &, QObject *)>(7, 2, QMC::AccessPublic, 0x80000000 | 6, {{
            { QMetaType::QObjectStar, 8 }, { QMetaType::QObjectStar, 9 }, { QMetaType::QObjectStar, 10 }, { QMetaType::QObjectStar, 3 },
            { QMetaType::QObjectStar, 11 }, { QMetaType::QObjectStar, 12 }, { QMetaType::QString, 13 }, { QMetaType::QString, 14 },
            { QMetaType::QObjectStar, 15 },
        }}),
        // Method 'retireProcess'
        QtMocHelpers::MethodData<QVariantMap(QObject *, QObject *, QObject *, QObject *, QObject *, QObject *, const QVariant &, QObject *)>(16, 2, QMC::AccessPublic, 0x80000000 | 6, {{
            { QMetaType::QObjectStar, 8 }, { QMetaType::QObjectStar, 9 }, { QMetaType::QObjectStar, 10 }, { QMetaType::QObjectStar, 3 },
            { QMetaType::QObjectStar, 11 }, { QMetaType::QObjectStar, 12 }, { 0x80000000 | 17, 4 }, { QMetaType::QObjectStar, 15 },
        }}),
        // Method 'processState'
        QtMocHelpers::MethodData<QVariantMap(QObject *, QObject *)>(18, 2, QMC::AccessPublic, 0x80000000 | 6, {{
            { QMetaType::QObjectStar, 3 }, { QMetaType::QObjectStar, 15 },
        }}),
        // Method 'cancelProcess'
        QtMocHelpers::MethodData<QVariantMap(QObject *, QObject *)>(19, 2, QMC::AccessPublic, 0x80000000 | 6, {{
            { QMetaType::QObjectStar, 3 }, { QMetaType::QObjectStar, 15 },
        }}),
        // Method 'observePopup'
        QtMocHelpers::MethodData<QVariantMap(QQuickItem *, QQuickItem *, QObject *, QObject *)>(20, 2, QMC::AccessPublic, 0x80000000 | 6, {{
            { 0x80000000 | 21, 8 }, { 0x80000000 | 21, 9 }, { QMetaType::QObjectStar, 10 }, { QMetaType::QObjectStar, 15 },
        }}),
        // Method 'observe'
        QtMocHelpers::MethodData<QVariantMap(QQuickItem *, QQuickItem *, QObject *)>(22, 2, QMC::AccessPublic, 0x80000000 | 6, {{
            { 0x80000000 | 21, 23 }, { 0x80000000 | 21, 24 }, { QMetaType::QObjectStar, 15 },
        }}),
    };
    QtMocHelpers::UintData qt_properties {
    };
    QtMocHelpers::UintData qt_enums {
    };
    return QtMocHelpers::metaObjectData<ObjectLifetimeProvider, qt_meta_tag_ZN22ObjectLifetimeProviderE_t>(QMC::MetaObjectFlag{}, qt_stringData,
            qt_methods, qt_properties, qt_enums);
}
Q_CONSTINIT const QMetaObject ObjectLifetimeProvider::staticMetaObject = { {
    QMetaObject::SuperData::link<QObject::staticMetaObject>(),
    qt_staticMetaObjectStaticContent<qt_meta_tag_ZN22ObjectLifetimeProviderE_t>.stringdata,
    qt_staticMetaObjectStaticContent<qt_meta_tag_ZN22ObjectLifetimeProviderE_t>.data,
    qt_static_metacall,
    nullptr,
    qt_staticMetaObjectRelocatingContent<qt_meta_tag_ZN22ObjectLifetimeProviderE_t>.metaTypes,
    nullptr
} };

void ObjectLifetimeProvider::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    auto *_t = static_cast<ObjectLifetimeProvider *>(_o);
    if (_c == QMetaObject::InvokeMetaMethod) {
        switch (_id) {
        case 0: _t->processLifecycleChanged((*reinterpret_cast<std::add_pointer_t<QObject*>>(_a[1])),(*reinterpret_cast<std::add_pointer_t<qulonglong>>(_a[2]))); break;
        case 1: { QVariantMap _r = _t->engineScope();
            if (_a[0]) *reinterpret_cast<QVariantMap*>(_a[0]) = std::move(_r); }  break;
        case 2: { QVariantMap _r = _t->armProcess((*reinterpret_cast<std::add_pointer_t<QObject*>>(_a[1])),(*reinterpret_cast<std::add_pointer_t<QObject*>>(_a[2])),(*reinterpret_cast<std::add_pointer_t<QObject*>>(_a[3])),(*reinterpret_cast<std::add_pointer_t<QObject*>>(_a[4])),(*reinterpret_cast<std::add_pointer_t<QObject*>>(_a[5])),(*reinterpret_cast<std::add_pointer_t<QObject*>>(_a[6])),(*reinterpret_cast<std::add_pointer_t<QString>>(_a[7])),(*reinterpret_cast<std::add_pointer_t<QString>>(_a[8])),(*reinterpret_cast<std::add_pointer_t<QObject*>>(_a[9])));
            if (_a[0]) *reinterpret_cast<QVariantMap*>(_a[0]) = std::move(_r); }  break;
        case 3: { QVariantMap _r = _t->retireProcess((*reinterpret_cast<std::add_pointer_t<QObject*>>(_a[1])),(*reinterpret_cast<std::add_pointer_t<QObject*>>(_a[2])),(*reinterpret_cast<std::add_pointer_t<QObject*>>(_a[3])),(*reinterpret_cast<std::add_pointer_t<QObject*>>(_a[4])),(*reinterpret_cast<std::add_pointer_t<QObject*>>(_a[5])),(*reinterpret_cast<std::add_pointer_t<QObject*>>(_a[6])),(*reinterpret_cast<std::add_pointer_t<QVariant>>(_a[7])),(*reinterpret_cast<std::add_pointer_t<QObject*>>(_a[8])));
            if (_a[0]) *reinterpret_cast<QVariantMap*>(_a[0]) = std::move(_r); }  break;
        case 4: { QVariantMap _r = _t->processState((*reinterpret_cast<std::add_pointer_t<QObject*>>(_a[1])),(*reinterpret_cast<std::add_pointer_t<QObject*>>(_a[2])));
            if (_a[0]) *reinterpret_cast<QVariantMap*>(_a[0]) = std::move(_r); }  break;
        case 5: { QVariantMap _r = _t->cancelProcess((*reinterpret_cast<std::add_pointer_t<QObject*>>(_a[1])),(*reinterpret_cast<std::add_pointer_t<QObject*>>(_a[2])));
            if (_a[0]) *reinterpret_cast<QVariantMap*>(_a[0]) = std::move(_r); }  break;
        case 6: { QVariantMap _r = _t->observePopup((*reinterpret_cast<std::add_pointer_t<QQuickItem*>>(_a[1])),(*reinterpret_cast<std::add_pointer_t<QQuickItem*>>(_a[2])),(*reinterpret_cast<std::add_pointer_t<QObject*>>(_a[3])),(*reinterpret_cast<std::add_pointer_t<QObject*>>(_a[4])));
            if (_a[0]) *reinterpret_cast<QVariantMap*>(_a[0]) = std::move(_r); }  break;
        case 7: { QVariantMap _r = _t->observe((*reinterpret_cast<std::add_pointer_t<QQuickItem*>>(_a[1])),(*reinterpret_cast<std::add_pointer_t<QQuickItem*>>(_a[2])),(*reinterpret_cast<std::add_pointer_t<QObject*>>(_a[3])));
            if (_a[0]) *reinterpret_cast<QVariantMap*>(_a[0]) = std::move(_r); }  break;
        default: ;
        }
    }
    if (_c == QMetaObject::RegisterMethodArgumentMetaType) {
        switch (_id) {
        default: *reinterpret_cast<QMetaType *>(_a[0]) = QMetaType(); break;
        case 6:
            switch (*reinterpret_cast<int*>(_a[1])) {
            default: *reinterpret_cast<QMetaType *>(_a[0]) = QMetaType(); break;
            case 1:
            case 0:
                *reinterpret_cast<QMetaType *>(_a[0]) = QMetaType::fromType< QQuickItem* >(); break;
            }
            break;
        case 7:
            switch (*reinterpret_cast<int*>(_a[1])) {
            default: *reinterpret_cast<QMetaType *>(_a[0]) = QMetaType(); break;
            case 1:
            case 0:
                *reinterpret_cast<QMetaType *>(_a[0]) = QMetaType::fromType< QQuickItem* >(); break;
            }
            break;
        }
    }
    if (_c == QMetaObject::IndexOfMethod) {
        if (QtMocHelpers::indexOfMethod<void (ObjectLifetimeProvider::*)(QObject * , qulonglong )>(_a, &ObjectLifetimeProvider::processLifecycleChanged, 0))
            return;
    }
}

const QMetaObject *ObjectLifetimeProvider::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->dynamicMetaObject() : &staticMetaObject;
}

void *ObjectLifetimeProvider::qt_metacast(const char *_clname)
{
    if (!_clname) return nullptr;
    if (!strcmp(_clname, qt_staticMetaObjectStaticContent<qt_meta_tag_ZN22ObjectLifetimeProviderE_t>.strings))
        return static_cast<void*>(this);
    return QObject::qt_metacast(_clname);
}

int ObjectLifetimeProvider::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QObject::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 8)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 8;
    }
    if (_c == QMetaObject::RegisterMethodArgumentMetaType) {
        if (_id < 8)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 8;
    }
    return _id;
}

// SIGNAL 0
void ObjectLifetimeProvider::processLifecycleChanged(QObject * _t1, qulonglong _t2)
{
    QMetaObject::activate<void>(this, &staticMetaObject, 0, nullptr, _t1, _t2);
}
QT_WARNING_POP
